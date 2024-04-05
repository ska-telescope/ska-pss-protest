@rfim
Feature: Tests of detection capability of CPU-based SPS pipeline with RFI Mitigation turned ON

    Scenario Outline: Detecting single pulses with rfim
        Given A 60 second <test_vector> containing single pulses
        And A basic cheetah configuration to ingest test vector and write single pulses candidate file
        And IQRM RFIM turned on with some threshold 3.0

        When An SPS pipeline runs
        Then Candidate metadata file is produced which contains detections of input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.00125_100.0_0.0_Gaussian_50.0_0000_123123123.fil  |
