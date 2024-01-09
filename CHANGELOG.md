# Changelog

## [v0.6.1](https://github.com/pyapp-kit/superqt/tree/v0.6.1) (2023-10-10)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.6.0...v0.6.1)

**Implemented enhancements:**

- feat: add QIcon backed by iconify [\#209](https://github.com/pyapp-kit/superqt/pull/209) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- ci: test python 3.12 [\#181](https://github.com/pyapp-kit/superqt/pull/181) ([tlambert03](https://github.com/tlambert03))

## [v0.6.0](https://github.com/pyapp-kit/superqt/tree/v0.6.0) (2023-09-25)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.5.4...v0.6.0)

**Implemented enhancements:**

- feat: add support for flag enum [\#207](https://github.com/pyapp-kit/superqt/pull/207) ([Czaki](https://github.com/Czaki))
- Add restart\_timer argument to GenericSignalThrottler.flush [\#206](https://github.com/pyapp-kit/superqt/pull/206) ([Czaki](https://github.com/Czaki))
- Add colormap combobox and utils [\#195](https://github.com/pyapp-kit/superqt/pull/195) ([tlambert03](https://github.com/tlambert03))
- feat: add QColorComboBox for picking single colors [\#194](https://github.com/pyapp-kit/superqt/pull/194) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- Fix IntEnum for python 3.11 [\#205](https://github.com/pyapp-kit/superqt/pull/205) ([Czaki](https://github.com/Czaki))
- fix: don't reuse text in qcollapsible [\#204](https://github.com/pyapp-kit/superqt/pull/204) ([tlambert03](https://github.com/tlambert03))
- fix: sliderMoved event on RangeSliders [\#200](https://github.com/pyapp-kit/superqt/pull/200) ([tlambert03](https://github.com/tlambert03))

**Documentation updates:**

- docs: add colormap utils and QSearchableTreeWidget to docs [\#199](https://github.com/pyapp-kit/superqt/pull/199) ([tlambert03](https://github.com/tlambert03))
- docs: update fonticon docs [\#198](https://github.com/pyapp-kit/superqt/pull/198) ([tlambert03](https://github.com/tlambert03))

**Tests & CI:**

- ci: \[pre-commit.ci\] autoupdate [\#193](https://github.com/pyapp-kit/superqt/pull/193) ([pre-commit-ci[bot]](https://github.com/apps/pre-commit-ci))

**Refactors:**

- refactor: Labeled slider updates [\#197](https://github.com/pyapp-kit/superqt/pull/197) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- ci\(dependabot\): bump actions/checkout from 3 to 4 [\#196](https://github.com/pyapp-kit/superqt/pull/196) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v0.5.4](https://github.com/pyapp-kit/superqt/tree/v0.5.4) (2023-08-31)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.5.3...v0.5.4)

**Fixed bugs:**

- fix: fix mysterious segfault [\#192](https://github.com/pyapp-kit/superqt/pull/192) ([tlambert03](https://github.com/tlambert03))

## [v0.5.3](https://github.com/pyapp-kit/superqt/tree/v0.5.3) (2023-08-21)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.5.2...v0.5.3)

**Implemented enhancements:**

- feat: add error `exceptions_as_dialog` context manager to catch and show Exceptions [\#191](https://github.com/pyapp-kit/superqt/pull/191) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- fix: remove dupes/aliases in QEnumCombo [\#190](https://github.com/pyapp-kit/superqt/pull/190) ([tlambert03](https://github.com/tlambert03))

## [v0.5.2](https://github.com/pyapp-kit/superqt/tree/v0.5.2) (2023-08-18)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.5.1...v0.5.2)

**Implemented enhancements:**

- feat: allow throttler/debouncer as method decorator [\#188](https://github.com/pyapp-kit/superqt/pull/188) ([Czaki](https://github.com/Czaki))

**Fixed bugs:**

- fix: Add descriptive exception when fail to add instance to weakref dictionary  [\#189](https://github.com/pyapp-kit/superqt/pull/189) ([Czaki](https://github.com/Czaki))

## [v0.5.1](https://github.com/pyapp-kit/superqt/tree/v0.5.1) (2023-08-17)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.5.0...v0.5.1)

**Fixed bugs:**

- fix: fix parameter inspection on ensure\_thread decorators \(alternate\) [\#185](https://github.com/pyapp-kit/superqt/pull/185) ([tlambert03](https://github.com/tlambert03))
- fix: fix callback of throttled/debounced decorated functions with mismatched args [\#184](https://github.com/pyapp-kit/superqt/pull/184) ([tlambert03](https://github.com/tlambert03))

**Documentation updates:**

- docs: document signals blocked [\#186](https://github.com/pyapp-kit/superqt/pull/186) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- test: change wait pattern [\#187](https://github.com/pyapp-kit/superqt/pull/187) ([tlambert03](https://github.com/tlambert03))
- build: drop python3.7, misc updates to repo [\#180](https://github.com/pyapp-kit/superqt/pull/180) ([tlambert03](https://github.com/tlambert03))

## [v0.5.0](https://github.com/pyapp-kit/superqt/tree/v0.5.0) (2023-08-06)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.4.1...v0.5.0)

**Implemented enhancements:**

- feat: add stepType to largeInt spinbox [\#179](https://github.com/pyapp-kit/superqt/pull/179) ([tlambert03](https://github.com/tlambert03))
- Searchable tree widget from a mapping [\#158](https://github.com/pyapp-kit/superqt/pull/158) ([andy-sweet](https://github.com/andy-sweet))
- Add `QElidingLineEdit` class for elidable `QLineEdit`s [\#154](https://github.com/pyapp-kit/superqt/pull/154) ([dalthviz](https://github.com/dalthviz))

**Fixed bugs:**

- fix: focus events on QLabeledSlider [\#175](https://github.com/pyapp-kit/superqt/pull/175) ([tlambert03](https://github.com/tlambert03))
- Set parent of timer in throttler [\#171](https://github.com/pyapp-kit/superqt/pull/171) ([Czaki](https://github.com/Czaki))
- fix: fix double slider label editing [\#168](https://github.com/pyapp-kit/superqt/pull/168) ([tlambert03](https://github.com/tlambert03))

**Documentation updates:**

- Fix typos [\#147](https://github.com/pyapp-kit/superqt/pull/147) ([kianmeng](https://github.com/kianmeng))

**Tests & CI:**

- tests: add qtbot to test to fix windows segfault [\#165](https://github.com/pyapp-kit/superqt/pull/165) ([tlambert03](https://github.com/tlambert03))
- test: fixing tests \[wip\] [\#164](https://github.com/pyapp-kit/superqt/pull/164) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- build: unpin pyside6.5 [\#178](https://github.com/pyapp-kit/superqt/pull/178) ([tlambert03](https://github.com/tlambert03))
- build: pin pyside6 to \<6.5.1 [\#169](https://github.com/pyapp-kit/superqt/pull/169) ([tlambert03](https://github.com/tlambert03))
- pin pyside6\<6.5 [\#160](https://github.com/pyapp-kit/superqt/pull/160) ([tlambert03](https://github.com/tlambert03))
- ci: \[pre-commit.ci\] autoupdate [\#146](https://github.com/pyapp-kit/superqt/pull/146) ([pre-commit-ci[bot]](https://github.com/apps/pre-commit-ci))

## [v0.4.1](https://github.com/pyapp-kit/superqt/tree/v0.4.1) (2022-12-01)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.4.0...v0.4.1)

**Implemented enhancements:**

- feat: Add signal to QCollapsible [\#142](https://github.com/pyapp-kit/superqt/pull/142) ([ppwadhwa](https://github.com/ppwadhwa))
- feat: Change icon used in Collapsible widget [\#140](https://github.com/pyapp-kit/superqt/pull/140) ([ppwadhwa](https://github.com/ppwadhwa))

**Fixed bugs:**

- Move QCollapsible toggle signal emit [\#144](https://github.com/pyapp-kit/superqt/pull/144) ([ppwadhwa](https://github.com/ppwadhwa))

**Merged pull requests:**

- build: use hatch for build backend, and use ruff for linting [\#139](https://github.com/pyapp-kit/superqt/pull/139) ([tlambert03](https://github.com/tlambert03))
- chore: rename napari org to pyapp-kit [\#137](https://github.com/pyapp-kit/superqt/pull/137) ([tlambert03](https://github.com/tlambert03))

## [v0.4.0](https://github.com/pyapp-kit/superqt/tree/v0.4.0) (2022-11-09)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.8...v0.4.0)

**Fixed bugs:**

- fix: fix quantity set value and add test [\#131](https://github.com/pyapp-kit/superqt/pull/131) ([tlambert03](https://github.com/tlambert03))

**Refactors:**

- refactor: update pyproject and ci, add py3.11 test [\#132](https://github.com/pyapp-kit/superqt/pull/132) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- chore: changelog v0.4.0 [\#136](https://github.com/pyapp-kit/superqt/pull/136) ([tlambert03](https://github.com/tlambert03))
- ci\(dependabot\): bump actions/upload-artifact from 2 to 3 [\#135](https://github.com/pyapp-kit/superqt/pull/135) ([dependabot[bot]](https://github.com/apps/dependabot))
- ci\(dependabot\): bump codecov/codecov-action from 2 to 3 [\#134](https://github.com/pyapp-kit/superqt/pull/134) ([dependabot[bot]](https://github.com/apps/dependabot))
- build: unpin pyside6 [\#133](https://github.com/pyapp-kit/superqt/pull/133) ([tlambert03](https://github.com/tlambert03))

## [v0.3.8](https://github.com/pyapp-kit/superqt/tree/v0.3.8) (2022-10-10)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.7...v0.3.8)

**Fixed bugs:**

- fix: allow submodule imports [\#128](https://github.com/pyapp-kit/superqt/pull/128) ([kne42](https://github.com/kne42))

## [v0.3.7](https://github.com/pyapp-kit/superqt/tree/v0.3.7) (2022-10-10)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.6...v0.3.7)

**Implemented enhancements:**

- feat: add Quantity widget \(using pint\) [\#126](https://github.com/pyapp-kit/superqt/pull/126) ([tlambert03](https://github.com/tlambert03))

## [v0.3.6](https://github.com/pyapp-kit/superqt/tree/v0.3.6) (2022-10-05)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.6rc0...v0.3.6)

**Documentation updates:**

- minor fix to readme [\#125](https://github.com/pyapp-kit/superqt/pull/125) ([tlambert03](https://github.com/tlambert03))
- Docs [\#124](https://github.com/pyapp-kit/superqt/pull/124) ([tlambert03](https://github.com/tlambert03))

## [v0.3.6rc0](https://github.com/pyapp-kit/superqt/tree/v0.3.6rc0) (2022-10-03)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.5...v0.3.6rc0)

**Implemented enhancements:**

- feat: add editing finished signal to LabeledSliders [\#122](https://github.com/pyapp-kit/superqt/pull/122) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- fix: fix missing labels after setValue [\#123](https://github.com/pyapp-kit/superqt/pull/123) ([tlambert03](https://github.com/tlambert03))
- fix: Fix TypeError on slider rangeChanged signal [\#121](https://github.com/pyapp-kit/superqt/pull/121) ([tlambert03](https://github.com/tlambert03))
- Simple workaround for pyside 6 [\#119](https://github.com/pyapp-kit/superqt/pull/119) ([Czaki](https://github.com/Czaki))
- fix: Offer patch for \(unstyled\) QSliders on macos 12 and Qt \<6 [\#117](https://github.com/pyapp-kit/superqt/pull/117) ([tlambert03](https://github.com/tlambert03))

## [v0.3.5](https://github.com/pyapp-kit/superqt/tree/v0.3.5) (2022-08-17)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.4...v0.3.5)

**Fixed bugs:**

- fix range slider drag crash on PyQt6 [\#108](https://github.com/pyapp-kit/superqt/pull/108) ([sfhbarnett](https://github.com/sfhbarnett))
- Fix float value error in pyqt configuration [\#106](https://github.com/pyapp-kit/superqt/pull/106) ([mstabrin](https://github.com/mstabrin))

**Merged pull requests:**

- chore: changelog v0.3.5 [\#110](https://github.com/pyapp-kit/superqt/pull/110) ([tlambert03](https://github.com/tlambert03))

## [v0.3.4](https://github.com/pyapp-kit/superqt/tree/v0.3.4) (2022-07-24)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.3...v0.3.4)

**Fixed bugs:**

- fix: relax runtime typing extensions requirement [\#101](https://github.com/pyapp-kit/superqt/pull/101) ([tlambert03](https://github.com/tlambert03))
- fix: catch qpixmap deprecation [\#99](https://github.com/pyapp-kit/superqt/pull/99) ([tlambert03](https://github.com/tlambert03))

## [v0.3.3](https://github.com/pyapp-kit/superqt/tree/v0.3.3) (2022-07-10)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.2...v0.3.3)

**Implemented enhancements:**

- Add code syntax highlight utils [\#88](https://github.com/pyapp-kit/superqt/pull/88) ([Czaki](https://github.com/Czaki))

**Fixed bugs:**

- fix: fix deprecation warning on fonticon plugin discovery on python 3.10 [\#95](https://github.com/pyapp-kit/superqt/pull/95) ([tlambert03](https://github.com/tlambert03))

## [v0.3.2](https://github.com/pyapp-kit/superqt/tree/v0.3.2) (2022-05-03)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.1...v0.3.2)

**Implemented enhancements:**

- Add QSearchableListWidget and QSearchableComboBox widgets [\#80](https://github.com/pyapp-kit/superqt/pull/80) ([Czaki](https://github.com/Czaki))

**Fixed bugs:**

- Fix crazy animation loop on Qcollapsible [\#84](https://github.com/pyapp-kit/superqt/pull/84) ([tlambert03](https://github.com/tlambert03))
- Reorder label update signal [\#83](https://github.com/pyapp-kit/superqt/pull/83) ([tlambert03](https://github.com/tlambert03))
- Fix height of expanded QCollapsible when child changes size [\#72](https://github.com/pyapp-kit/superqt/pull/72) ([tlambert03](https://github.com/tlambert03))

**Tests & CI:**

- Fix deprecation warnings in tests [\#82](https://github.com/pyapp-kit/superqt/pull/82) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- Add changelog for v0.3.2 [\#86](https://github.com/pyapp-kit/superqt/pull/86) ([tlambert03](https://github.com/tlambert03))

## [v0.3.1](https://github.com/pyapp-kit/superqt/tree/v0.3.1) (2022-03-02)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.3.0...v0.3.1)

**Implemented enhancements:**

- Add `signals_blocked` util [\#69](https://github.com/pyapp-kit/superqt/pull/69) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- put SignalInstance in TYPE\_CHECKING clause, check min requirements [\#70](https://github.com/pyapp-kit/superqt/pull/70) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- Add changelog for v0.3.1 [\#71](https://github.com/pyapp-kit/superqt/pull/71) ([tlambert03](https://github.com/tlambert03))

## [v0.3.0](https://github.com/pyapp-kit/superqt/tree/v0.3.0) (2022-02-16)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.5-1...v0.3.0)

**Implemented enhancements:**

- Qthrottler and debouncer [\#62](https://github.com/pyapp-kit/superqt/pull/62) ([tlambert03](https://github.com/tlambert03))
- add edgeLabelMode option to QLabeledSlider [\#59](https://github.com/pyapp-kit/superqt/pull/59) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- Fix nested threadworker not starting [\#63](https://github.com/pyapp-kit/superqt/pull/63) ([tlambert03](https://github.com/tlambert03))
- Add missing signals on proxy sliders  [\#54](https://github.com/pyapp-kit/superqt/pull/54) ([tlambert03](https://github.com/tlambert03))
- Ugly but functional workaround for pyside6.2.1 breakages [\#51](https://github.com/pyapp-kit/superqt/pull/51) ([tlambert03](https://github.com/tlambert03))

**Tests & CI:**

- add napari test to CI [\#67](https://github.com/pyapp-kit/superqt/pull/67) ([tlambert03](https://github.com/tlambert03))
- add gh-release action [\#65](https://github.com/pyapp-kit/superqt/pull/65) ([tlambert03](https://github.com/tlambert03))
- fix xvfb tests [\#61](https://github.com/pyapp-kit/superqt/pull/61) ([tlambert03](https://github.com/tlambert03))

**Refactors:**

- Use qtpy, deprecate superqt.qtcompat, drop support for Qt \<5.12 [\#39](https://github.com/pyapp-kit/superqt/pull/39) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- Add changelog for v0.3.0 [\#68](https://github.com/pyapp-kit/superqt/pull/68) ([tlambert03](https://github.com/tlambert03))

## [v0.2.5-1](https://github.com/pyapp-kit/superqt/tree/v0.2.5-1) (2021-11-23)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.5...v0.2.5-1)

**Merged pull requests:**

- typing-extensions version pinning [\#46](https://github.com/pyapp-kit/superqt/pull/46) ([AhmetCanSolak](https://github.com/AhmetCanSolak))

## [v0.2.5](https://github.com/pyapp-kit/superqt/tree/v0.2.5) (2021-11-22)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.4...v0.2.5)

**Implemented enhancements:**

- add support for python 3.10 [\#42](https://github.com/pyapp-kit/superqt/pull/42) ([tlambert03](https://github.com/tlambert03))
- QCollapsible for Collapsible Section Control [\#37](https://github.com/pyapp-kit/superqt/pull/37) ([MosGeo](https://github.com/MosGeo))
- Threadworker [\#31](https://github.com/pyapp-kit/superqt/pull/31) ([tlambert03](https://github.com/tlambert03))
- Add font icons [\#24](https://github.com/pyapp-kit/superqt/pull/24) ([tlambert03](https://github.com/tlambert03))

**Fixed bugs:**

- Fix some small linting issues. [\#41](https://github.com/pyapp-kit/superqt/pull/41) ([tlambert03](https://github.com/tlambert03))
- Use functools.wraps insterad of \_\_wraped\_\_ and manual proxing \_\_name\_\_ [\#29](https://github.com/pyapp-kit/superqt/pull/29) ([Czaki](https://github.com/Czaki))
- Propagate function name in `ensure_main_thread` and `ensure_object_thread` [\#28](https://github.com/pyapp-kit/superqt/pull/28) ([Czaki](https://github.com/Czaki))

**Tests & CI:**

- reskip test\_object\_thread\_return on ci [\#43](https://github.com/pyapp-kit/superqt/pull/43) ([tlambert03](https://github.com/tlambert03))

**Refactors:**

- refactoring qtcompat [\#34](https://github.com/pyapp-kit/superqt/pull/34) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- Fix-manifest, move font tests [\#44](https://github.com/pyapp-kit/superqt/pull/44) ([tlambert03](https://github.com/tlambert03))
- update deploy [\#33](https://github.com/pyapp-kit/superqt/pull/33) ([tlambert03](https://github.com/tlambert03))
- move to src layout [\#32](https://github.com/pyapp-kit/superqt/pull/32) ([tlambert03](https://github.com/tlambert03))

## [v0.2.4](https://github.com/pyapp-kit/superqt/tree/v0.2.4) (2021-09-13)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.3...v0.2.4)

**Implemented enhancements:**

- Add type stubs for ensure\_thread decorator [\#23](https://github.com/pyapp-kit/superqt/pull/23) ([tlambert03](https://github.com/tlambert03))
- Add `ensure_main_tread` and `ensure_object_thread` [\#22](https://github.com/pyapp-kit/superqt/pull/22) ([Czaki](https://github.com/Czaki))
- Add QMessageHandler context manager [\#21](https://github.com/pyapp-kit/superqt/pull/21) ([tlambert03](https://github.com/tlambert03))

**Merged pull requests:**

- add changelog for 0.2.4 [\#25](https://github.com/pyapp-kit/superqt/pull/25) ([tlambert03](https://github.com/tlambert03))

## [v0.2.3](https://github.com/pyapp-kit/superqt/tree/v0.2.3) (2021-08-25)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.2...v0.2.3)

**Fixed bugs:**

- Fix warnings on eliding label for 5.12, test more qt versions [\#19](https://github.com/pyapp-kit/superqt/pull/19) ([tlambert03](https://github.com/tlambert03))

## [v0.2.2](https://github.com/pyapp-kit/superqt/tree/v0.2.2) (2021-08-17)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.1...v0.2.2)

**Implemented enhancements:**

- Add QElidingLabel [\#16](https://github.com/pyapp-kit/superqt/pull/16) ([tlambert03](https://github.com/tlambert03))
- Enum ComboBox implementation [\#13](https://github.com/pyapp-kit/superqt/pull/13) ([Czaki](https://github.com/Czaki))

**Documentation updates:**

- fix broken link [\#18](https://github.com/pyapp-kit/superqt/pull/18) ([haesleinhuepf](https://github.com/haesleinhuepf))

## [v0.2.1](https://github.com/pyapp-kit/superqt/tree/v0.2.1) (2021-07-10)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.0rc0...v0.2.1)

**Fixed bugs:**

- Fix QLabeledRangeSlider API \(fix slider proxy\) [\#10](https://github.com/pyapp-kit/superqt/pull/10) ([tlambert03](https://github.com/tlambert03))
- Fix range slider with negative min range [\#9](https://github.com/pyapp-kit/superqt/pull/9) ([tlambert03](https://github.com/tlambert03))

## [v0.2.0rc0](https://github.com/pyapp-kit/superqt/tree/v0.2.0rc0) (2021-06-26)

[Full Changelog](https://github.com/pyapp-kit/superqt/compare/v0.2.0...v0.2.0rc0)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
