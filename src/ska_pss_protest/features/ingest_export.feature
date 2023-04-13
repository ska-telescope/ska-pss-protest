@product
Feature: Ingest and export of test vector data
    PSS pipeline exports filterbank data with correct properties

    Scenario Outline: Exporting filterbank data
        Given A PSS <test_vector>
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to export filterbanked data

        When The cheetah pipeline runs
        Then The exported filterbank data is identical to the ingested filterbank data

        Examples:
        | test_vector                                                       |
        | FDAS-HSUM-MID_38d46df_500.0_0.05_1.0_100.397_Gaussian_50.0_123123123.fil |
        | FDAS-HSUM-MID_acf46ab_50.0_0.05_1.0_200.0_Gaussian_50.0_123123123.fil    |
