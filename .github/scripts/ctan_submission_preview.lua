local version = arg[1]
local archive_path = arg[2]
local announcement_path = arg[3]
local checksum = arg[4]

local function fail(message)
  io.stderr:write(message .. "\n")
  os.exit(1)
end

if not version or not version:match("^%d+%.%d+%.%d+$") then
  fail("A semantic package version is required.")
end
if not archive_path or not announcement_path then
  fail("Archive and announcement paths are required.")
end
if not checksum or not checksum:match("^%x%x+$") or #checksum ~= 64 then
  fail("A SHA-256 archive checksum is required.")
end

dofile("build.lua")
local metadata = uploadconfig
if not metadata then
  fail("CTAN upload metadata is missing.")
end

local required_fields = {
  author = metadata.author,
  ctanPath = metadata.ctanPath,
  license = metadata.license,
  pkg = metadata.pkg,
  summary = metadata.summary,
  uploader = metadata.uploader,
}
for name, value in pairs(required_fields) do
  if value == nil or value == "" then
    fail("Required CTAN metadata is missing: " .. name)
  end
end

local archive = io.open(archive_path, "rb")
if not archive then
  fail("The CTAN archive is missing: " .. archive_path)
end
local archive_size = archive:seek("end")
archive:close()
if not archive_size or archive_size == 0 then
  fail("The CTAN archive is empty.")
end

local announcement_file = io.open(announcement_path, "rb")
if not announcement_file then
  fail("The CTAN announcement file is missing.")
end
local announcement = announcement_file:read("*a")
announcement_file:close()
if not announcement:match("%S") then
  fail("The CTAN announcement is empty.")
end
if #announcement > 8192 then
  fail("The CTAN announcement exceeds the 8192-byte limit.")
end

local function escape_html(value)
  return tostring(value)
    :gsub("&", "&amp;")
    :gsub("<", "&lt;")
    :gsub(">", "&gt;")
end

local license = metadata.license
if type(license) == "table" then
  license = table.concat(license, ", ")
end

io.write("## CTAN submission preview\n\n")
io.write("- **Package:** `" .. escape_html(metadata.pkg) .. "`\n")
io.write("- **Version:** `" .. escape_html(version) .. "`\n")
io.write("- **Author:** " .. escape_html(metadata.author) .. "\n")
io.write("- **Uploader:** " .. escape_html(metadata.uploader) .. "\n")
io.write(
  "- **Uploader email:** "
    .. (metadata.email and metadata.email ~= "" and "configured (redacted)" or "not configured")
    .. "\n"
)
io.write("- **CTAN path:** `" .. escape_html(metadata.ctanPath) .. "`\n")
io.write("- **License:** " .. escape_html(license) .. "\n")
io.write("- **Summary:** " .. escape_html(metadata.summary) .. "\n")
io.write("- **Description:** " .. escape_html(metadata.description or "") .. "\n")
io.write("- **Archive:** `" .. escape_html(archive_path:match("([^/]+)$")) .. "`\n")
io.write("- **Archive size:** " .. archive_size .. " bytes\n")
io.write("- **SHA-256:** `" .. checksum .. "`\n\n")
io.write("### Announcement\n\n<pre>\n")
io.write(escape_html(announcement))
io.write("\n</pre>\n")
