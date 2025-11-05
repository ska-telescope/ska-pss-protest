# Changelog
## 5.2.5
- Added a module to read OCLD files. This reader is provides a `Pandas.DataFrame` of all the candidates' metadata and also extracts individual candidate data.

## 5.2.4
- Fixing indentation in feature file for SPS tests

## 5.2.3
- Setting right version numbers for ProTest
- Disabling RequesterTests due to network reset issues

## 5.2.2
- Included code to account for downsampling in SPS candidate validators with corresponding downsampling factor in the dedispersion plan
- Modified SPS tests to use updated cheetah config
- Added tests to use multiple SPS clustering (Friends-of-friends and HDBScan) and sifting (Thresholding and RF-sift) algorithms

## 5.2.1
- Modifying the SPS emulator test to use updated naming scheme of test vectors

## 5.2.0
- Updating the naming scheme of the test vectors to include red noise parameters
- Updating product tests to include the test vectors with updated naming scheme

## 5.1.6
- Disabled S/N Tolerance for FDAS tests

## 5.1.4
- Added RFIM-FDAS test using Labyrinth

## 5.1.3
- Updating FDAS product test feature file to use Basic tolerance ruleset

## 5.1.2
- Realistic tolerances defined for FDAS search validator
- Functionality to choose a tolerance set for validation in the FDAS test feature file
- Additional unit tests to test the updated validator classes

## 5.1.1
- Adding tags to FDAS test feature file

## 5.1.0

- Adding CPU-FDAS (Labyrinth) test
- Modifying configuration file template to run CPU-FDAS
- Fixing expected SCL file format to match the one exported by Cheetah
- Changes in unit tests to accommodate updated SCL file format

## 5.0.5

- Adding a test to SPS-MID-RFIM for broadband RFI excision

## 5.0.4

- Updating versions in all necessary files

## 5.0.3

- Added functionality to export S/N of detected candidate to summary file
- Increased the SIGPROC buffer size for RFIM-SPS tests

## 5.0.2

- Added capability to run a subset of test (e.g., for MRs or quick tests)

## 5.0.1

- Expose all pytest options to ProTest executable

## 5.0.0

- Source code restructure
- Improvements to protest menu/options descriptions

## 4.1.2

- Adding functionality to export summary of RFIM tests
- Fixing a bug to switch off the filterbank writer from v4.1.1

## 4.1.1

- Adding SPS-RFIM tests
