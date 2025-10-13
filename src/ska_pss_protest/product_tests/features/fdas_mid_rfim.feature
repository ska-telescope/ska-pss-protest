Feature: Tests of detection capability of CPU-based FDAS pipeline.

    @all @rfim-fdas
    Scenario Outline: Detecting pulsars
        Given A 600 second duration <test_vector> containing a pulsar
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to configure CPU-FDAS pipeline and export the FDAS candidate metadata
        And A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata
        And A IQRM RFIM enabled with threshold of <threshold> and radius of <radius>

        When A FDAS pipeline runs
        Then A FDAS candidates metadata file is produced which is validate using <tol_settings> tolerances

        Examples:
        | test_vector                                                       |   threshold   |   radius  |   tol_settings    |
        | FLDO-MID_6fbbb58_54_0.1_100_0_Gaussian_40.0_pkmk_0.0_0.0_123123.fil	    |   3           |   400     |   basic           |
