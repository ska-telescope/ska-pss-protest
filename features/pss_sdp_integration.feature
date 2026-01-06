@pss-sdp-interface @integration @end-to-end
Feature: PSS-SDP End-to-End Integration
  As an SKA system integrator
  I want to verify the complete PSS to SDP data flow
  So that the interface meets operational requirements

  Background:
    Given the PSS Cheetah pipeline is deployed
    And the SDP pss-receive component is deployed
    And network connectivity exists between PSS and SDP

  @XTP-TBD @happy-path @smoke
  Scenario: Complete single pulse candidate transmission from PSS to SDP
    Given the PSS pipeline is processing beamformed data
    And the SDP receiver is listening for candidate data
    When a single pulse candidate is detected by PSS
    Then the candidate is serialised for network transmission
    And the candidate is transmitted to SDP
    And the SDP receiver ingests the candidate data
    And the candidate metadata is stored in the persistent volume

  @XTP-TBD @data-rate
  Scenario: Interface handles expected data rates
    Given the CBF beamformer generates data at a known data rate
    When PSS processes the data and detects candidates
    Then candidate metadata is transmitted at the expected rate
    And the SDP receiver processes all incoming candidates
    And no candidate data is lost during normal operation

  @XTP-TBD @data-rate @stress
  Scenario Outline: Interface handles maximum data rates
    Given the CBF beamformer generates data at <data_rate> Gbps
    When PSS processes the data at maximum throughput
    Then candidate metadata transmission keeps pace with detection rate
    And the SDP receiver processes all incoming candidates without backpressure
    And CPU utilisation remains below <cpu_limit> percent
    And memory utilisation remains below <memory_limit> percent
    And no candidate data is lost under maximum load

    Examples:
      | data_rate | cpu_limit | memory_limit |
      | 10        | 80        | 75           |
      | 25        | 90        | 85           |
      | 50        | 95        | 90           |

  @XTP-TBD @multi-beam
  Scenario: Handle candidate data from multiple beams
    Given multiple PSS beams are configured
    And each beam is processing independent data streams
    When candidates are detected across multiple beams
    Then each beam's candidates are exported with beam identification
    And the SDP receiver distinguishes candidates by beam
    And candidate storage is organised by beam identifier

  @XTP-TBD @protocol-compatibility
  Scenario: Verify protocol compatibility between PSS and SDP
    Given PSS uses the Cheetah network streamer
    And SDP uses the corresponding network reader
    When candidate data is transmitted
    Then the protocol versions are compatible
    And data descriptors are correctly interpreted
    And no protocol negotiation errors occur

  @XTP-TBD @deployment-verification
  Scenario: Verify Kubernetes deployment of interface components
    Given the Helm charts for PSS and pss-receive are deployed
    When the deployments are verified
    Then the PSS pipeline pod is running
    And the pss-receive job is running
    And the pss-receive service is exposing UDP port 9021
    And the persistent volume claim is bound

  @XTP-TBD @observation-session
  Scenario: Process candidate data throughout an observation session
    Given an observation session is scheduled
    When the session begins and beamformed data is received
    Then candidate detection runs continuously
    And candidate export operates throughout the session
    And all detected candidates are received by SDP
    And the session completes without data loss

  @XTP-TBD @calibration-integration
  Scenario: Apply calibration data during candidate processing
    Given calibration matrices are available from CBF
    When the PSS pipeline processes beamformed data
    Then calibration is applied to the data
    And candidate detection uses calibrated data
    And calibration parameters are included in candidate metadata

  @XTP-TBD @latency-requirements
  Scenario Outline: Meet latency requirements for real-time candidate transmission
    Given real-time processing requirements define a maximum latency of <max_latency_ms> milliseconds
    When a candidate is detected by the pipeline
    Then the candidate is transmitted within <transmission_budget_ms> milliseconds
    And the SDP receiver ingests the candidate within <ingestion_budget_ms> milliseconds
    And end-to-end latency is below <max_latency_ms> milliseconds

    Examples:
      | max_latency_ms | transmission_budget_ms | ingestion_budget_ms |
      | 100            | 50                     | 50                  |

  @XTP-TBD @monitoring-integration
  Scenario: Monitor interface health and performance
    Given monitoring is configured for the PSS-SDP interface
    When the interface is operational
    Then candidate transmission rates are recorded
    And packet loss statistics are available
    And error rates are tracked and reported
    And alerts are raised for anomalous conditions
