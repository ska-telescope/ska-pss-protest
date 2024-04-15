@rfim-sps
Feature: Tests of detection capability of CPU-based SPS pipeline with RFI Mitigation turned ON

    
    Scenario Outline: Detecting single pulses with rfim
        Given A 60 second duration SPS-MID-RFI Test-vector containing <freq> single pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width> and folded S/N of <sn> with RFI configuration <rfi>
        And A basic cheetah configuration to ingest test vector and export single pulse candidate metadata to file
        And IQRM RFIM enabled with threshold of <threshold> and radius of <radius>.

        When An SPS pipeline runs
        Then Validate the Candidate metadata file produced

        Examples:
        | freq  | dm    | width | sn    | rfi   | threshold | radius    |
        | 0.125 | 100   | 0.1   | 150   | 0000  | 3.0       | 100       |
        | 0.125 | 100   | 0.1   | 150   | 7Lha  | 3.0       | 100       |
    