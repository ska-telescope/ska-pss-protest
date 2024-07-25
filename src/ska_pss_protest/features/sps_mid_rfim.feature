@rfim-sps @product @cpu @sps @testvector @positive @mid @physhw @nasm @xfail
Feature: Tests of detection capability of CPU-based SPS pipeline with RFI Mitigation turned ON

    
    Scenario Outline: Detecting single pulses with RFIM using IQRM
        Given A 60 second duration SPS-MID-RFI Test-vector containing <freq> single pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width> and folded S/N of <sn> with RFI configuration <rfi>
        And A basic cheetah configuration to ingest test vector and export single pulse candidate metadata to file
        And IQRM RFIM enabled with threshold of <threshold> and radius of <radius>

        When An SPS pipeline runs
        Then all injected pulses are recovered according the candidate metadata produced

        Examples:
        | freq  | dm    | width | sn    | rfi   | threshold | radius    |
        | 0.125 | 100   | 0.01  | 150   | 0000  | 3.0       | 400       |
        | 0.125 | 100   | 0.01  | 150   | 7svk  | 3.0       | 400       |

    Scenario Outline: Detecting single pulses with RFIM using Sum-Threshold
        Given A 60 second duration SPS-MID-RFI Test-vector containing <freq> single pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width> and folded S/N of <sn> with RFI configuration <rfi>
        And A basic cheetah configuration to ingest test vector and export single pulse candidate metadata to file
        And Sum-Threshold RFIM enabled with cutoff of <cutoff> and window size of <window>

        When An SPS pipeline runs
        Then all injected pulses are recovered according the candidate metadata produced

        Examples:
        | freq  | dm    | width | sn    | rfi   | cutoff    | window    |
        | 0.125 | 100   | 0.01  | 150   | 0000  | 3.0       | 32        |
        | 0.125 | 100   | 0.01  | 150   | 7svk  | 3.0       | 32        |
    