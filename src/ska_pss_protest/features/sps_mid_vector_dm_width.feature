@product @cpu @sps @testvector
Feature: Tests of detection capability of a CPU-based SPS pipeline in dm-width parameter space
    SPS pipeline exports filterbanks and candidate lists corresponding to injected single-pulses covering multiple dispersion measures and pulse widths
    

    Scenario: Detecting single pulses
        Given A 60 second duration <type> test vector containing "0.125" pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width> and a S/N of "14"
        And A cheetah configuration to ingest the test vector
        And A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata

        When An SPS pipeline runs
        Then Candidate filterbanks and metadata are exported and written to disk

        Examples:
        | type    | dm     | width     |
        | SPS-MID | 1.0    | 0.0000125 |
        | SPS-MID | 1.0    | 0.00215   |
        | SPS-MID | 1.0    | 0.125     |
        | SPS-MID | 100.0  | 0.0000125 |
        | SPS-MID | 100.0  | 0.00215   |
        | SPS-MID | 100.0  | 0.125     |
        | SPS-MID | 370.0  | 0.0000125 |
        | SPS-MID | 370.0  | 0.00215   |
        | SPS-MID | 370.0  | 0.125     |
        | SPS-MID | 500.0  | 0.0000125 |
        | SPS-MID | 500.0  | 0.00215   |
        | SPS-MID | 500.0  | 0.125     |
        | SPS-MID | 740.0  | 0.0000125 |
        | SPS-MID | 740.0  | 0.00215   |
        | SPS-MID | 740.0  | 0.125     |
        | SPS-MID | 1000.0 | 0.0000125 |
        | SPS-MID | 1000.0 | 0.00215   |
        | SPS-MID | 1000.0 | 0.125     |
        | SPS-MID | 1480.0 | 0.0000125 |
        | SPS-MID | 1480.0 | 0.00215   |
        | SPS-MID | 1480.0 | 0.125     |
        | SPS-MID | 2000.0 | 0.0000125 |
        | SPS-MID | 2000.0 | 0.00215   |
        | SPS-MID | 2000.0 | 0.125     |
        | SPS-MID | 2950.0 | 0.0000125 |
        | SPS-MID | 2950.0 | 0.00215   |
        | SPS-MID | 2950.0 | 0.125     |
        | SPS-MID | 3000.0 | 0.0000125 |
        | SPS-MID | 3000.0 | 0.00215   |
        | SPS-MID | 3000.0 | 0.125     |
