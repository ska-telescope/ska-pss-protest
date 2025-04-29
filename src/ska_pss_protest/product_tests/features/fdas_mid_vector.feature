Feature: Tests of detection capability of CPU-based FDAS pipeline.

    @product @cpu @fdas @nasm @all @testvector @mid @labyrinth
    Scenario Outline: Detecting pulsars
        Given A 600 second duration <test_vector> containing a pulsar
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to configure CPU-FDAS pipeline and export the FDAS candidate metadata
        And A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata

        When A FDAS pipeline runs
        Then A FDAS candidates metadata file is produced which is validate using <tol_settings> tolerances

        Examples:
        | test_vector                                                       |   tol_settings    |
        | FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil   |   dummy           |

