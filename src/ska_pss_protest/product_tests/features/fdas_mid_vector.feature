Feature: Tests of detection capability of CPU-based FDAS pipeline.

    @product @cpu @fdas @nasm @all @testvector @mid @labyrinth @overnight @nonaccelerated
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
        | FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_0.0_0.0_123123.fil   |   basic           | short             |

    @product @cpu @fdas @nasm @all @testvector @mid @labyrinth @nonaccelerated @fortnight
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
        | FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_0.0_0.0_123123.fil   |   basic           |       short       |
        | FLDO-MID_6cbfdfb_42_0.05_100_0.0_Gaussian_100.0_0000_0.0_0.0_123123.fil   |   basic           |       short       |
        | FDAS-ACC-MID_b78c926_50_0.3_10_0.0_Gaussian_27.0_0000_0.0_0.0_XXXX.fil    |   basic           |       short       |
        | FDAS-ACC-MID_b78c926_200_0.05_10_0.0_Gaussian_27.0_0000_0.0_0.0_XXXX.fil  |   basic           |       short       |

    @product @fdas @fpga @all @testvector @mid @short @accelerated @overnight
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

    @product @fdas @fpga @all @testvector @mid @short @accelerated @fortnight
    Scenario Outline: Detecting pulsars
        Given A 600 second duration <test_vector> containing a pulsar
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to configure FPGA-FDAS pipeline and export the FDAS candidate metadata
        And A cheetah configuration to set up FLDO module
        And A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata

        When A FDAS pipeline runs using <dedispersion_plan>
        Then A FDAS candidates metadata file is produced which is validate using <tol_settings> tolerances

        Examples:
        | test_vector                                                                   |   tol_settings    | dedispersion_plan |
        | FDAS-ACC-MID_b78c926_20_0.05_10_50.0_Gaussian_27.0_0000_0.0_0.0_XXXX.fil      |       basic       |       short       |
        | FDAS-ACC-MID_b78c926_200_0.05_100_350.0_Gaussian_14.0_0000_0.0_0.0_XXXX.fil   |       basic       |       short       |

