CREATE TABLE event_store_messages_partitioned
(
  uuid        uuid DEFAULT gen_random_uuid() NOT NULL,
  kind        character varying              NOT NULL,
  data        jsonb,
  "time"      timestamp WITHOUT TIME ZONE    NOT NULL,
  parent_uuid uuid
) PARTITION BY RANGE ("time");

ALTER TABLE event_store_messages_partitioned
  ADD CONSTRAINT event_store_messages_partitioned_pkey PRIMARY KEY (uuid, "time");