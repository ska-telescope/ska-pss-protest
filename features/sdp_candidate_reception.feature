@pss-sdp-interface @sdp-receive @data-ingestion
Feature: SDP Reception of PSS Candidate Data
  As an SDP data processor
  I want to receive candidate data from PSS
  So that candidate metadata can be stored and analysed

  Background:
    Given the SDP pss-receive component is deployed
    And the receiver is listening on the configured port

  @XTP-TBD @happy-path
  Scenario Outline: Receive single pulse candidate data from PSS
    Given the pss-receive service is running on port <port>
    When PSS transmits single pulse candidate data
    Then the receiver ingests the data payload
    And the candidate metadata is extracted from the payload

    #placeholder values
    Examples:
      | port |
      | 9021 |

  @XTP-TBD @data-storage
  Scenario: Store received candidate metadata to persistent volume
    #placeholder variable for mount path
    Given the persistent volume is mounted at "/home/pss2sdp/receive/output" 
    When candidate metadata is received from PSS
    Then the metadata is written to the persistent volume
    And the data persists beyond the receiver container lifecycle

  @XTP-TBD @spccl-reception
  Scenario: Receive SPCCL formatted candidate data
    Given the receiver is configured to accept SPCCL data
    When SPCCL candidate data is transmitted from PSS
    Then the receiver stores the data with ".spccl" extension
    And the file contents match the transmitted data

  @XTP-TBD @kubernetes-service
  Scenario: SDP receiver is accessible via Kubernetes service
    #placeholder values
    Given the pss-receive service is deployed in the pss namespace
    And the ClusterIP service exposes UDP port 9021
    When PSS sends data to the service DNS name "pss-receive"
    Then the data is routed to the receiver pod
    And the receiver processes the incoming data

  @XTP-TBD @receiver-initialisation
  Scenario: Receiver initialises Cheetah data exporter successfully
    Given the pss-receive container is starting
    When the Cheetah data exporter initialises
    Then the log shows the sp_candidate_data sink is created
    And the receiver is ready to accept incoming data

  @XTP-TBD @job-completion
  Scenario: Receiver job runs until completion or timeout
    #placeholder value for active deadline seconds
    Given the pss-receive job has an active deadline of 3600 seconds
    When the receiver is processing data
    Then the job continues running until the deadline
    And data received before the deadline is persisted

  @XTP-TBD @candidate-fields-extraction
  Scenario: Extract individual candidate fields from received data
    Given the receiver has ingested a data payload containing candidate data
    When the payload is deserialised
    Then the dispersion measure is extracted in pc/cm3 units
    And the sigma significance is extracted
    And the signal-to-noise ratio is extracted
    And the pulse width is extracted in milliseconds
    And the pulse time is extracted

  @XTP-TBD @volume-capacity
  Scenario: Verify persistent volume has sufficient capacity
    #placeholder values for storage
    Given the persistent volume claim requests 1 GiB of storage
    When candidate data is received over an extended period
    Then the storage capacity is sufficient for the observation duration
    And no data loss occurs due to storage exhaustion

  @XTP-TBD @parallel-reception
  Scenario: Handle multiple concurrent data streams
    Given multiple PSS beams are configured to send data
    When candidate data arrives from multiple beams simultaneously
    Then the receiver processes all incoming streams
    And candidate data from each beam is stored separately
