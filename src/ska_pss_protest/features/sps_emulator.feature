@product
Feature: Sps emulator
    A simple emulator of SPS data products

    Scenario: Detecting fake single pulses
        Given A 60s test vector containing random noise
        And A candidate generation rate of 1 per second

        When The SPS pipeline runs
        Then 60 candidates are written to SpCcl file
