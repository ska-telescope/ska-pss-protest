Feature: Tests of detection capability of a CPU-based SPS pipeline.

    @product @cpu @sps @all @testvector @positive @mid @physhw @nasm
    Scenario Outline: Detecting single pulses
        Given A 60 second duration <test_vector> containing single pulses
	And A cheetah configuration to ingest the test vector
	And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata

	When An SPS pipeline runs
	Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
	And A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_1.25e-05_1.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_1.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.125_1.0_0.0_Gaussian_50.0_0000_123123123.fil      |
        | SPS-MID_747e95f_0.125_1.25e-05_100.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.00125_100.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_100.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_370.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_370.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_500.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_500.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_740.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_740.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_1000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_1000.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_2000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_2000.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_2950.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_2950.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil   |

    @product @cpu @subset @testvector @positive @mid @physhw @nasm
    Scenario Outline: Detecting single pulses subset
        Given A 60 second duration <test_vector> containing single pulses
	And A cheetah configuration to ingest the test vector
	And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata

	When An SPS pipeline runs
	Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
	And A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.00125_500.0_0.0_Gaussian_50.0_0000_123123123.fil  |

    @product @cpu @sps @all @testvector @positive @mid @physhw @nasm
    Scenario Outline: Detecting single pulses using filters
        Given A 60 second duration <test_vector> containing single pulses
	And A cheetah configuration to ingest the test vector
	And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata
	And A cheetah configuration to cluster SPS candidate metadata using FOF clustering algorithm
    And A cheetah configuration to sift SPS candidate metadata using thresholding algorithm

	When An SPS pipeline runs
	Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
	Then A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.00125_740.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_740.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil   |


    @product @cpu @sps @all @testvector @positive @mid @physhw @nasm
    Scenario Outline: Detecting single pulses using filters
        Given A 60 second duration <test_vector> containing single pulses
	And A cheetah configuration to ingest the test vector
	And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata
	And A cheetah configuration to cluster SPS candidate metadata using HDBScan clustering algorithm
    And A cheetah configuration to sift SPS candidate metadata using thresholding algorithm

	When An SPS pipeline runs
	Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
	Then A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.00125_740.0_0.0_Gaussian_50.0_0000_123123123.fil  |
        | SPS-MID_747e95f_0.125_0.125_740.0_0.0_Gaussian_50.0_0000_123123123.fil    |
        | SPS-MID_747e95f_0.125_0.00125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil   |
        | SPS-MID_747e95f_0.125_0.00125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil |
        | SPS-MID_747e95f_0.125_0.125_3000.0_0.0_Gaussian_50.0_0000_123123123.fil   |


    @product @cpu @subset @testvector @positive @mid @physhw @nasm
    Scenario Outline: Detecting single pulses using filters subset
        Given A 60 second duration <test_vector> containing single pulses
	And A cheetah configuration to ingest the test vector
	And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata
	And A cheetah configuration to cluster SPS candidate metadata using FOF clustering algorithm
    And A cheetah configuration to sift SPS candidate metadata using thresholding algorithm

	When An SPS pipeline runs
	Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
	Then A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | test_vector                                                               |
        | SPS-MID_747e95f_0.125_0.125_1480.0_0.0_Gaussian_50.0_0000_123123123.fil   |
