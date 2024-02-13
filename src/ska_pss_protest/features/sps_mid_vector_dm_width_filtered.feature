@product @cpu @sps @testvector @positive @mid @nasm @physhw
Feature: Tests of detection capability of a CPU-based SPS pipeline in dm-width parameter space with sifting and clustering enabled
    SPS pipeline exports filterbanks and candidate lists corresponding to injected single-pulses covering multiple dispersion measures and pulse widths

    Scenario Outline: Detecting single pulses using filters
        Given A 60 second duration <test_vector> containing single pulses
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to sift and cluster SPS candidate metadata

        When An SPS pipeline runs
        Then A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.00125_740.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_740.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil   |
