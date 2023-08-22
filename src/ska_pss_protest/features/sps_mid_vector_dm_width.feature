@product @cpu @sps @testvector @positive @mid @nasm
Feature: Tests of detection capability of a CPU-based SPS pipeline in dm-width parameter space
    SPS pipeline exports filterbanks and candidate lists corresponding to injected single-pulses covering multiple dispersion measures and pulse widths

    Scenario Outline: Detecting single pulses
        Given A 60 second duration <vector_type> containing <freq> pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width> and a combined S/N of <sn>
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata

        When An SPS pipeline runs
        Then Candidate filterbanks are exported to disk and their header properties are consistent with the test vector
        And A candidate metadata file is produced which contains detections of the input signals

        Examples:
        | vector_type | dm     | width     | freq  | sn |
        | SPS-MID     | 1.0    | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 1.0    | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 1.0    | 0.125     | 0.125 | 50 |
        | SPS-MID     | 100.0  | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 100.0  | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 100.0  | 0.125     | 0.125 | 50 |
        | SPS-MID     | 370.0  | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 370.0  | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 370.0  | 0.125     | 0.125 | 50 |
        | SPS-MID     | 500.0  | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 500.0  | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 500.0  | 0.125     | 0.125 | 50 |
        | SPS-MID     | 740.0  | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 740.0  | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 740.0  | 0.125     | 0.125 | 50 |
        | SPS-MID     | 1000.0 | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 1000.0 | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 1000.0 | 0.125     | 0.125 | 50 |
        | SPS-MID     | 1480.0 | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 1480.0 | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 1480.0 | 0.125     | 0.125 | 50 |
        | SPS-MID     | 2000.0 | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 2000.0 | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 2000.0 | 0.125     | 0.125 | 50 |
        | SPS-MID     | 2950.0 | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 2950.0 | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 2950.0 | 0.125     | 0.125 | 50 |
        | SPS-MID     | 3000.0 | 0.0000125 | 0.125 | 50 |
        | SPS-MID     | 3000.0 | 0.00125   | 0.125 | 50 |
        | SPS-MID     | 3000.0 | 0.125     | 0.125 | 50 |
