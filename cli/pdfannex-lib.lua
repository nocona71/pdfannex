-- Shared helpers for the pdfannex CLI and its bundled resolver.
-- Project-owned wrappers for JSON, hashing, filesystem and process execution
-- (spec/10): the rest of the code never touches these primitives directly.
local M = {}
local windows = package.config:sub(1, 1) == "\\"

local function powershell_quote(s)
  return "'" .. s:gsub("'", "''") .. "'"
end

local function powershell_encode(s)
  local bytes = {}
  for i = 1, #s do bytes[#bytes + 1] = string.char(s:byte(i), 0) end
  bytes = table.concat(bytes)
  local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
  local encoded = {}
  for i = 1, #bytes, 3 do
    local a, b, c = bytes:byte(i, i + 2)
    local n = a * 65536 + (b or 0) * 256 + (c or 0)
    local x, y, z, w = math.floor(n / 262144) % 64, math.floor(n / 4096) % 64,
      math.floor(n / 64) % 64, n % 64
    encoded[#encoded + 1] = alphabet:sub(x + 1, x + 1)
    encoded[#encoded + 1] = alphabet:sub(y + 1, y + 1)
    encoded[#encoded + 1] = b and alphabet:sub(z + 1, z + 1) or "="
    encoded[#encoded + 1] = c and alphabet:sub(w + 1, w + 1) or "="
  end
  return table.concat(encoded)
end

---------------------------------------------------------------- JSON
local escapes = { ['"'] = '\\"', ['\\'] = '\\\\', ['\b'] = '\\b', ['\f'] = '\\f',
                  ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t' }

local function encode_string(s)
  return '"' .. s:gsub('[%c"\\]', function(c)
    return escapes[c] or string.format("\\u%04x", c:byte())
  end) .. '"'
end

local function is_array(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  return n == #t
end

-- Keys are sorted so output is deterministic (lockfile diffs stay small).
local function encode(v, indent, level)
  local t = type(v)
  if t == "string" then return encode_string(v) end
  if t == "number" or t == "boolean" then return tostring(v) end
  if t ~= "table" then error("cannot encode " .. t) end
  local nl, pad, padc, sep = "", "", "", ","
  if indent then
    nl = "\n"
    pad = string.rep(indent, level + 1)
    padc = string.rep(indent, level)
  end
  local parts = {}
  if next(v) == nil then return "[]" end
  if is_array(v) then
    for i, x in ipairs(v) do parts[i] = pad .. encode(x, indent, level + 1) end
    return "[" .. nl .. table.concat(parts, sep .. nl) .. nl .. padc .. "]"
  end
  local keys = {}
  for k in pairs(v) do keys[#keys + 1] = k end
  table.sort(keys)
  local colon = indent and ": " or ":"
  for i, k in ipairs(keys) do
    parts[i] = pad .. encode_string(k) .. colon .. encode(v[k], indent, level + 1)
  end
  return "{" .. nl .. table.concat(parts, sep .. nl) .. nl .. padc .. "}"
end

function M.json_encode(v, pretty)
  return encode(v, pretty and "  " or nil, 0)
end

function M.json_decode(s)
  local pos = 1
  local function fail(msg) error("invalid JSON at byte " .. pos .. ": " .. msg, 0) end
  local function skip() pos = s:find("[^ \t\r\n]", pos) or #s + 1 end
  local value
  local function str()
    local out = {}
    pos = pos + 1
    while true do
      local c = s:sub(pos, pos)
      if c == "" then fail("unterminated string") end
      if c == '"' then pos = pos + 1; return table.concat(out) end
      if c == "\\" then
        local e = s:sub(pos + 1, pos + 1)
        local map = { b = "\b", f = "\f", n = "\n", r = "\r", t = "\t",
                      ['"'] = '"', ["\\"] = "\\", ["/"] = "/" }
        if e == "u" then
          local hex = s:match("^%x%x%x%x", pos + 2) or fail("bad \\u escape")
          out[#out + 1] = utf8.char(tonumber(hex, 16))
          pos = pos + 6
        elseif map[e] then
          out[#out + 1] = map[e]; pos = pos + 2
        else fail("bad escape") end
      else
        out[#out + 1] = c; pos = pos + 1
      end
    end
  end
  function value()
    skip()
    local c = s:sub(pos, pos)
    if c == "{" then
      local obj = {}
      pos = pos + 1; skip()
      if s:sub(pos, pos) == "}" then pos = pos + 1; return obj end
      while true do
        skip()
        if s:sub(pos, pos) ~= '"' then fail("object key expected") end
        local k = str(); skip()
        if s:sub(pos, pos) ~= ":" then fail("':' expected") end
        pos = pos + 1
        obj[k] = value(); skip()
        local d = s:sub(pos, pos); pos = pos + 1
        if d == "}" then return obj end
        if d ~= "," then fail("',' or '}' expected") end
      end
    elseif c == "[" then
      local arr = {}
      pos = pos + 1; skip()
      if s:sub(pos, pos) == "]" then pos = pos + 1; return arr end
      while true do
        arr[#arr + 1] = value(); skip()
        local d = s:sub(pos, pos); pos = pos + 1
        if d == "]" then return arr end
        if d ~= "," then fail("',' or ']' expected") end
      end
    elseif c == '"' then return str()
    elseif s:find("^true", pos) then pos = pos + 4; return true
    elseif s:find("^false", pos) then pos = pos + 5; return false
    elseif s:find("^null", pos) then pos = pos + 4; return nil
    else
      local num = s:match("^-?%d+%.?%d*[eE]?[+-]?%d*", pos)
      if not num or num == "" then fail("unexpected character") end
      pos = pos + #num
      return tonumber(num)
    end
  end
  local result = value()
  skip()
  if pos <= #s then fail("trailing data") end
  return result
end

---------------------------------------------------------------- files
function M.normalize_path(path)
  return path:gsub("\\", "/")
end

function M.is_absolute(path)
  path = M.normalize_path(path)
  return path:sub(1, 1) == "/" or path:match("^%a:") ~= nil
end

function M.read_file(path)
  local f, err = io.open(path, "rb")
  if not f then return nil, err end
  local data = f:read("a")
  f:close()
  return data
end

function M.write_file(path, data)
  local f, err = io.open(path, "wb")
  if not f then return nil, err end
  f:write(data)
  f:flush()
  f:close()
  return true
end

function M.exists(path)
  return lfs.attributes(path, "mode") ~= nil
end

function M.mkdirs(path)
  path = M.normalize_path(path)
  local root = path:match("^%a:/") and path:sub(1, 3)
    or path:sub(1, 1) == "/" and "/"
    or ""
  local cur = root
  for part in path:sub(#root + 1):gmatch("[^/]+") do
    if cur == "" or cur:sub(-1) == "/" then
      cur = cur .. part
    else
      cur = cur .. "/" .. part
    end
    if not M.exists(cur) then
      local ok, err = lfs.mkdir(cur)
      if not ok then return nil, err end
    end
  end
  return true
end

function M.dirname(path)
  path = M.normalize_path(path)
  return path:match("^(.*)/[^/]*$") or "."
end

local function absolute_path(path)
  path = M.normalize_path(path)
  if M.is_absolute(path) then return path end
  return M.normalize_path(lfs.currentdir() .. "/" .. path)
end

-- Write to a temporary sibling and rename, so readers never see a partial file.
function M.atomic_write(path, data)
  local tmp = path .. ".tmp"
  local ok, err = M.write_file(tmp, data)
  if not ok then return nil, err end
  local renamed, rename_err = os.rename(tmp, path)
  if renamed or not windows or not M.exists(path) then return renamed, rename_err end
  local command = "[IO.File]::Replace(" .. powershell_quote(absolute_path(tmp)) .. ","
    .. powershell_quote(absolute_path(path)) .. ",$null)"
  local replaced, code = M.run_process({
    "powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command,
  })
  if replaced then return true end
  return nil, tostring(rename_err) .. "; replacement failed with status " .. tostring(code)
end

function M.sha256_hex(data)
  return (sha2.digest256(data):gsub(".", function(c)
    return string.format("%02x", c:byte())
  end))
end

-- Plausible PDF: header near the start, end-of-file marker near the end.
function M.looks_like_pdf(data)
  return data:sub(1, 1024):find("%%PDF%-") ~= nil
     and data:sub(-1024):find("%%%%EOF") ~= nil
end

---------------------------------------------------------------- sources
-- pdfannex.sty exchanges sources hex-encoded (UTF-8 bytes), so any file name
-- is safe in the generated TeX files.
function M.hex_encode(s)
  return (s:gsub(".", function(c) return string.format("%02X", c:byte()) end))
end

function M.hex_decode(h)
  if #h % 2 ~= 0 or h:find("%X") then return nil end
  return (h:gsub("%x%x", function(x) return string.char(tonumber(x, 16)) end))
end

function M.pct_encode(s)
  return (s:gsub("[^%w%-%._~/]", function(c) return string.format("%%%02X", c:byte()) end))
end

function M.pct_decode(s)
  return (s:gsub("%%(%x%x)", function(x) return string.char(tonumber(x, 16)) end))
end

-- A plain path as written in \includeannex means pdfannex://file/<path>.
function M.normalize_source(src)
  if src:find("^pdfannex://") then return src end
  return "pdfannex://file/" .. M.pct_encode(src)
end

function M.source_scheme(src)
  return src:match("^pdfannex://([%w%-]+)/")
end

---------------------------------------------------------------- processes
local function quote_arg(s)
  return "'" .. s:gsub("'", "'\\''") .. "'"
end

local function quote_windows_arg(s)
  -- ProcessStartInfo.Arguments is parsed again by the target Windows process.
  local quoted, backslashes = { '"' }, 0
  for i = 1, #s do
    local char = s:sub(i, i)
    if char == "\\" then
      backslashes = backslashes + 1
    else
      if char == '"' then
        quoted[#quoted + 1] = string.rep("\\", backslashes * 2 + 1)
      else
        quoted[#quoted + 1] = string.rep("\\", backslashes)
      end
      quoted[#quoted + 1] = char
      backslashes = 0
    end
  end
  quoted[#quoted + 1] = string.rep("\\", backslashes * 2)
  quoted[#quoted + 1] = '"'
  return table.concat(quoted)
end

local function run_windows_process(command, input, output)
  local args = {}
  for i = 2, #command do
    args[#args + 1] = quote_windows_arg(command[i])
  end
  local request = M.json_encode({
    command = command[1],
    arguments = table.concat(args, " "),
    input = input,
    output = output,
  })
  local hex = request:gsub(".", function(c) return string.format("%02x", c:byte()) end)
  local bootstrap = "$h='" .. hex .. "'"
    .. ";$b=New-Object byte[] ([int]($h.Length/2))"
    .. ";for($i=0;$i -lt $h.Length;$i+=2){$b[$i/2]=[Convert]::ToByte($h.Substring($i,2),16)}"
    .. ";$spec=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString($b))"
    .. ";try{$ErrorActionPreference='Stop'"
    .. ";$psi=New-Object System.Diagnostics.ProcessStartInfo"
    .. ";$psi.FileName=[string]$spec.command"
    .. ";$psi.UseShellExecute=$false"
    .. ";$psi.RedirectStandardInput=($null -ne $spec.input)"
    .. ";$psi.RedirectStandardOutput=($null -ne $spec.output)"
    .. ";$psi.Arguments=[string]$spec.arguments"
    .. ";$p=New-Object System.Diagnostics.Process"
    .. ";$p.StartInfo=$psi"
    .. ";[void]$p.Start();$copy=$null"
    .. ";if($null -ne $spec.output){$out=[IO.File]::Create([string]$spec.output)"
    .. ";$copy=$p.StandardOutput.BaseStream.CopyToAsync($out)}"
    .. ";if($null -ne $spec.input){$infile=[IO.File]::OpenRead([string]$spec.input)"
    .. ";$infile.CopyTo($p.StandardInput.BaseStream);$infile.Dispose();$p.StandardInput.Close()}"
    .. ";$p.WaitForExit();if($null -ne $copy){$copy.Wait();$out.Dispose()}"
    .. ";exit $p.ExitCode}catch{[Console]::Error.WriteLine($_);exit 1}"
  local ok, why, code = os.execute(
    "powershell.exe -NoLogo -NoProfile -NonInteractive -EncodedCommand "
      .. powershell_encode(bootstrap))
  return ok == true or ok == 0, code or why
end

function M.run_process(command, input, output)
  if windows then return run_windows_process(command, input, output) end
  local quoted = {}
  for i, arg in ipairs(command) do
    quoted[i] = quote_arg(arg)
  end
  local cmd = table.concat(quoted, " ")
  if input then cmd = cmd .. " < " .. quote_arg(input) end
  if output then cmd = cmd .. " > " .. quote_arg(output) end
  local ok, why, code = os.execute(cmd)
  return ok == true or ok == 0, code or why
end

function M.find_resolver(name)
  local path_sep = windows and ";" or ":"
  local path = os.getenv("PATH") or ""
  for dir in (path .. path_sep):gmatch("(.-)" .. path_sep) do
    if dir == "" then dir = "." end
    local separator = "/"
    if dir:sub(-1) == "/" or dir:sub(-1) == "\\" then separator = "" end
    for _, suffix in ipairs({ "", ".lua" }) do
      local candidate = dir .. separator .. name .. suffix
      if lfs.attributes(candidate, "mode") == "file" then return candidate end
    end
  end
  if kpse and kpse.find_file then
    kpse.set_program_name("latex")
    for _, suffix in ipairs({ "", ".lua" }) do
      local found = kpse.find_file(name .. suffix, "texmfscripts")
      if found and lfs.attributes(found, "mode") == "file" then return found end
    end
  end
  return nil
end

-- Run a Resolver Protocol 1 script with JSON on stdin/stdout and diagnostics
-- left attached to stderr.
function M.run_resolver(exe, request)
  local reqfile, respfile = os.tmpname(), os.tmpname()
  local ok, err = M.write_file(reqfile, M.json_encode(request))
  if not ok then os.remove(reqfile); os.remove(respfile); return nil, err end
  local okexec, code = M.run_process({ "texlua", exe }, reqfile, respfile)
  local out = M.read_file(respfile)
  os.remove(reqfile); os.remove(respfile)
  if not okexec then
    return nil, "resolver exited with status " .. tostring(code)
  end
  local parsed, perr = pcall(M.json_decode, out or "")
  if not parsed then return nil, "resolver returned invalid JSON: " .. tostring(perr) end
  return perr
end

return M
