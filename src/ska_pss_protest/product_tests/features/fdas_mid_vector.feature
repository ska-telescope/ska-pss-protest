Feature: Tests of detection capability of CPU-based FDAS pipeline.

    @product @cpu @fdas @all @testvector @mid @labyrinth
    Scenario Outline: Detecting pulsars
        Given A 600 second duration <test_vector> containing a pulsars
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to export the SPS candidate metadata
        And A cheetah configuration to export the CPU-FDAS candidate metadata

    When An FDAS pipeline runs
    Then A FDAS candidates metadata file is produced wich contains detections of the input signals

        Examples:
        | test_vector                                                       |
        | FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil   |