@rfim
Feature: Tests of detection capability of CPU-based SPS pipeline with RFI Mitigation turned ON

    
    Scenario Outline: Detecting single pulses with rfim
        Given A 60 second duration Test-vector containing single pulses <freq> pulses per second, each with a dispersion measure of <dm>, a duty cycle of <width>, a combined S/N of <sn> with RFI-ID - <rfi>
        And A basic cheetah configuration to ingest test vector and write single pulses candidate file
        And IQRM RFIM turned on with threshold equal to 3.0 and radius of 100.

        When An SPS pipeline runs
        Then Candidate metadata file is produced which contains detections of input signals

        Examples:
        | freq  | dm    | width | sn    | rfi   |
        | 0.125 | 100   | 0.1   | 150   | 0000  |

