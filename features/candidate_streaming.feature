@pss-sdp-interface @streaming @network
Feature: PSS to SDP Candidate Data Streaming
  As a pulsar search system
  I want to stream candidate data to SDP using a network streaming protocol
  So that detected candidates are transmitted in real-time for further analysis

  Background:
    Given the PSS Cheetah pipeline is initialised
    And the network exporter is configured with a valid endpoint

  @AT4-2140 @happy-path
  Scenario: Stream single pulse candidate data to SDP
    Given single pulse candidates have been detected by the pipeline
    When the SpCcl data is sent to the configured network endpoint
    Then the candidate data is transmitted to the receiver
    And the data payload contains valid candidate metadata

  @AT4-2140 @happy-path
  Scenario: Transmitted data contains required candidate fields
    Given a single pulse candidate with known properties exists
    When the candidate is serialised for transmission
    Then the payload contains the dispersion measure field
    And the payload contains the signal-to-noise ratio field
    And the payload contains the candidate start time field
    And the payload contains the pulse width field
    And the payload contains the sigma significance field

  @AT4-2140 @happy-path
  Scenario: Transmitted data contains time-frequency data descriptors
    Given a single pulse candidate with associated time-frequency data exists
    When the candidate is serialised for transmission
    Then the payload contains the time-frequency data descriptor
    And the payload contains the frequency-time data descriptor
    And the payload contains channel metadata including frequency and width

  @AT4-2140 @configuration
  Scenario Outline: Configure network endpoint for candidate streaming
    Given the pipeline configuration contains network sink settings
    When the endpoint is configured with IP address "<ip_address>" and port "<port>"
    Then the network streamer connects to the specified endpoint
    And candidates are transmitted to that network address

    Examples:
      | ip_address      | port |
      | 192.168.1.100   | 9021 |
      | 10.0.0.50       | 9021 |
      | 172.16.0.1      | 9022 |

  @AT4-2140 @multiple-endpoints
  Scenario: Stream candidates to multiple network endpoints
    Given multiple network endpoints are configured in the sink configuration
    When single pulse candidates are detected
    Then the candidate data is transmitted to all configured endpoints
    And each endpoint receives identical candidate information

  @AT4-2140 @data-integrity
  Scenario: Transmitted candidate data maintains integrity
    Given a candidate with dispersion measure of 100.5 pc/cm3 exists
    And the candidate has a signal-to-noise ratio of 8.5
    When the candidate is transmitted to the receiver
    Then the received dispersion measure matches the original value
    And the received signal-to-noise ratio matches the original value

  @AT4-2140 @performance
  Scenario: Network streaming handles high candidate rates
    Given the pipeline is processing data at real-time rates
    When multiple candidates are detected within a short time window
    Then all candidates are queued for transmission
    And candidates are transmitted without significant delay
