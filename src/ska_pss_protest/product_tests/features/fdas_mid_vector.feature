Feature: Tests of detection capability of CPU-based FDAS pipeline.

    @product @cpu @fdas @nasm @all @testvector @mid @labyrinth
    Scenario Outline: Detecting non-accelerated pulsars
        Given A 600 second duration <test_vector> containing a pulsar
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to configure CPU-FDAS pipeline and export the FDAS candidate metadata
        And A cheetah configuration to set up FLDO module
        And A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata

        When A FDAS pipeline runs using <dedispersion_plan>
        Then A FDAS candidates metadata file is produced which is validate using <tol_settings> tolerances

        Examples:
        | test_vector                                                               |   tol_settings    | dedispersion_plan |
        | FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_0.0_0.0_123123.fil   |   basic           | generic           |

    @product @fdas @fpga @all @testvector @mid
    Scenario Outline: Detecting pulsars
        Given A 600 second duration <test_vector> containing a pulsar
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to configure FPGA-FDAS pipeline and export the FDAS candidate metadata
        And A cheetah configuration to set up FLDO module
        And A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata

        When A FDAS pipeline runs using <dedispersion_plan>
        Then A FDAS candidates metadata file is produced which is validate using <tol_settings> tolerances

        Examples:
        | test_vector                                                               |   tol_settings    | dedispersion_plan |
        | FDAS-ACC-MID_b78c926_20_0.05_10_50.0_Gaussian_27.0_0000_0.0_0.0_XXXX.fil  |   basic           | short             |

