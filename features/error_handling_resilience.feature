@pss-sdp-interface @error-handling @resilience
Feature: PSS-SDP Interface Error Handling and Resilience
  As a system operator
  I want the PSS-SDP interface to handle errors gracefully
  So that data transmission is reliable and failures are recoverable

  Background:
    Given the PSS-SDP interface is operational
    And monitoring is enabled for the data transmission

  @XTP-TBD @invalid-header
  Scenario: Handle packets with invalid headers
    Given data packets are being received by SDP
    When a packet with an invalid header arrives
    Then the invalid packet is discarded
    And an error is logged for diagnostic purposes
    And subsequent valid packets continue to be processed

  @XTP-TBD @network-unreachable
  Scenario: Handle network endpoint unreachable
    Given the network exporter is configured with an endpoint
    When the network endpoint becomes unreachable
    Then the exporter logs a connection error
    And candidate data is queued for retry if possible
    And the pipeline continues processing without blocking

  @XTP-TBD @packet-loss
  Scenario: Handle packet loss during transmission
    Given candidate data is being transmitted over the network
    When network congestion causes packet loss
    Then the streaming protocol handles incomplete data gracefully
    And lost data is identified through sequence number gaps
    And statistics on packet loss are recorded

  @XTP-TBD @receiver-restart
  Scenario: Recover from receiver pod restart
    Given the pss-receive pod is processing data
    When the pod is restarted due to failure or update
    Then the Kubernetes job manages pod recreation
    And the new pod resumes listening on the configured port
    And previously persisted data remains available

  @XTP-TBD @storage-exhaustion
  Scenario: Handle persistent volume storage exhaustion
    Given the receiver is writing to the persistent volume
    When the storage capacity is exhausted
    Then an error is logged indicating storage full
    And the receiver handles the write failure gracefully
    And operators are alerted to the storage condition

  @XTP-TBD @configuration-error
  Scenario: Handle invalid exporter configuration
    Given a pipeline configuration file is provided
    When the configuration contains an invalid sink type
    Then the pipeline reports a configuration error
    And the error message identifies the invalid setting
    And the pipeline fails fast with a clear error

  @XTP-TBD @deserialisation-error
  Scenario: Handle malformed data payload
    Given data payloads are being received
    When a payload contains malformed candidate data
    Then the deserialisation error is caught
    And the malformed payload is logged for investigation
    And the receiver continues processing subsequent payloads

  @XTP-TBD @job-deadline-exceeded
  Scenario: Handle receiver job deadline exceeded
    Given the pss-receive job has an active deadline
    When the job runs beyond the configured deadline
    Then Kubernetes terminates the job
    And data received before termination is persisted
    And the job status reflects the deadline exceeded condition

  @XTP-TBD @connection-retry
  Scenario: Retry connection to network endpoint on failure
    Given the network exporter encounters a connection failure
    When the connection retry mechanism is triggered
    Then the exporter attempts to reconnect after a delay
    And exponential backoff is applied to retry attempts
    And the maximum retry count is respected

  @XTP-TBD @resource-cleanup
  Scenario: Clean up resources on pipeline shutdown
    Given the PSS pipeline is processing data
    When the pipeline receives a shutdown signal
    Then pending candidate data is flushed to exporters
    And network connections are closed gracefully
    And file handles are properly released

  @XTP-TBD @duplicate-detection
  Scenario: Handle duplicate candidate data reception
    Given the SDP receiver is processing incoming data
    When duplicate data payloads arrive due to network issues
    Then duplicate payloads are identified by sequence numbers
    And duplicates are discarded or flagged
    And only unique candidate data is persisted

  @XTP-TBD @timeout-handling
  Scenario: Handle transmission timeout
    Given candidate data transmission is in progress
    When the transmission exceeds the configured timeout
    Then the operation is aborted
    And the timeout is logged with relevant context
    And the system attempts to recover and continue

  @XTP-TBD @error-handling @data-validation
  Scenario: Validate candidate data before transmission
    Given candidate data is ready for export
    When the data is validated before transmission
    Then candidates with invalid dispersion measure are flagged
    And candidates with out-of-range values are logged
    And valid candidates proceed to transmission
