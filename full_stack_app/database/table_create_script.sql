CREATE TABLE IF NOT EXISTS public.operations
(
    operation_id bigserial NOT NULL,
    operation_type character varying COLLATE pg_catalog."default" NOT NULL,
    number_1 double precision NOT NULL,
    number_2 double precision NOT NULL,
    operation_result double precision NOT NULL,
    CONSTRAINT "PK_operations__operation_id" PRIMARY KEY (operation_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.operations
    OWNER to admin_user;