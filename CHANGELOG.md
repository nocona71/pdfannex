# Changelog

## [0.7.4](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.7.3...pdfannex-v0.7.4) (2026-10-07)


### Bug Fixes

* guard first-time CTAN submissions ([#49](https://github.com/nocona71/pdfannex/issues/49)) ([dcbe101](https://github.com/nocona71/pdfannex/commit/dcbe1019724e2a220e4b69e768a43b2449ee8651))

## [0.7.3](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.7.2...pdfannex-v0.7.3) (2026-10-07)


### Bug Fixes

* install l3build for CTAN submission ([#47](https://github.com/nocona71/pdfannex/issues/47)) ([b6762a1](https://github.com/nocona71/pdfannex/commit/b6762a14a239222e7d4098651ed741e77d54e3b6))

## [0.7.2](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.7.1...pdfannex-v0.7.2) (2026-10-07)


### Bug Fixes

* bypass stalled Azure Ubuntu mirror ([#45](https://github.com/nocona71/pdfannex/issues/45)) ([f3007f4](https://github.com/nocona71/pdfannex/commit/f3007f45bb1b6ba7e9875df9b7ba6be6ef138cc9))

## [0.7.1](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.7.0...pdfannex-v0.7.1) (2026-10-07)


### Bug Fixes

* bound apt waits in GitHub Actions ([#44](https://github.com/nocona71/pdfannex/issues/44)) ([c7d9d2f](https://github.com/nocona71/pdfannex/commit/c7d9d2f12eae16f29c91c3c1528098bd27791782))
* upload versioned CTAN archive artifact ([#42](https://github.com/nocona71/pdfannex/issues/42)) ([d17d8bb](https://github.com/nocona71/pdfannex/commit/d17d8bb91ccf9719733c681927fcd41e9357a3c0))

## [0.7.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.6.2...pdfannex-v0.7.0) (2026-10-07)


### Features

* add manual CTAN submission review ([#39](https://github.com/nocona71/pdfannex/issues/39)) ([ce2bf09](https://github.com/nocona71/pdfannex/commit/ce2bf098d245663c6ea8a1c2c665c77e957daaa1))

## [0.6.2](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.6.1...pdfannex-v0.6.2) (2026-10-07)


### Bug Fixes

* include showcase assets in archive E2E ([#35](https://github.com/nocona71/pdfannex/issues/35)) ([c4e39ee](https://github.com/nocona71/pdfannex/commit/c4e39eea2a51dcf8181df2ecd38a43d944474e9d))

## [0.6.1](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.6.0...pdfannex-v0.6.1) (2026-10-07)


### Bug Fixes

* support references in moving PDF contexts ([#31](https://github.com/nocona71/pdfannex/issues/31)) ([444e339](https://github.com/nocona71/pdfannex/commit/444e339aaebd11b76e84cfd790c793ff74105d05))

## [0.6.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.5.1...pdfannex-v0.6.0) (2026-10-07)


### Features

* extract docstore adapter to nocona71/pdfannex-docstore ([#28](https://github.com/nocona71/pdfannex/issues/28)) ([f0942a0](https://github.com/nocona71/pdfannex/commit/f0942a007ad8e639a6cc95f407bfe3b2afe2b28a))

## [0.5.1](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.5.0...pdfannex-v0.5.1) (2026-10-07)


### Bug Fixes

* resolve annexes with latexmk output directories ([#24](https://github.com/nocona71/pdfannex/issues/24)) ([8f0de5f](https://github.com/nocona71/pdfannex/commit/8f0de5fbe5863b22eadeda65efe287f8cc39cdcb))

## [0.5.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.4.0...pdfannex-v0.5.0) (2026-10-07)


### Features

* add latexmk bootstrap and TDS installer ([#22](https://github.com/nocona71/pdfannex/issues/22)) ([f6ce871](https://github.com/nocona71/pdfannex/commit/f6ce871942841dd79da1b79a1b158b19b62a8a00))

## [0.4.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.3.1...pdfannex-v0.4.0) (2026-10-07)


### Features

* update CLI to report package version dynamically and enhance documentation ([266aeee](https://github.com/nocona71/pdfannex/commit/266aeeecb85669927a21767bbab58f2005283791))

## [0.3.1](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.3.0...pdfannex-v0.3.1) (2026-10-07)


### Bug Fixes

* safely invoke Windows PowerShell bootstrap ([5905a4b](https://github.com/nocona71/pdfannex/commit/5905a4b0c612a7388712a8bb3a1e14a7248e37ca))

## [0.3.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.2.0...pdfannex-v0.3.0) (2026-10-07)


### Features

* \NewAnnexSource and example docstore resolver ([5daad84](https://github.com/nocona71/pdfannex/commit/5daad8443f306289d2d5a31dca0561c352cba4b3))
* **cli:** add pdfannex CLI with lock, store and file resolver ([af72ea9](https://github.com/nocona71/pdfannex/commit/af72ea91a5dead8ac8054b13ae78fb6e6d7adffe))
* **cli:** hex-encoded source exchange for any file name; locked-mode test suite ([63f4b57](https://github.com/nocona71/pdfannex/commit/63f4b57da64e490d95d53dba87110c544305cbc1))
* **cli:** make request recording opt-in via pdfannex init ([5249e73](https://github.com/nocona71/pdfannex/commit/5249e739601f7c6233e84eab2492d2c4def85dab))
* HTTP docstore adapter example with mock server ([573a277](https://github.com/nocona71/pdfannex/commit/573a27798ebb21bc30146e844c7c36da0fe90b21))
* package docstore adapter for CTAN ([fee8c0e](https://github.com/nocona71/pdfannex/commit/fee8c0e2a76150f9fc555e08e39e11156ded1192))
* prepare docstore adapter for standalone packaging ([2e16fd2](https://github.com/nocona71/pdfannex/commit/2e16fd2ec516030272de1addfe371cabe52b6215))
* ship CLI in CTAN package ([e796ba7](https://github.com/nocona71/pdfannex/commit/e796ba76da33b585921c694f9b46dedddf03312a))

## [0.2.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.1.0...pdfannex-v0.2.0) (2026-10-06)


### Features

* add nup key for several source pages per sheet ([672f806](https://github.com/nocona71/pdfannex/commit/672f8060918d1a8e957a8702b101ca25f4e7ac95))

## [0.1.0](https://github.com/nocona71/pdfannex/compare/pdfannex-v0.1.0...pdfannex-v0.1.0) (2026-10-06)


### Miscellaneous Chores

* release 0.1.0 ([7082ce6](https://github.com/nocona71/pdfannex/commit/7082ce6fe35b18b42c99ca774328e938b27d4674))

## Changelog
