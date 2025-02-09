-- Table: public.image_data

-- DROP TABLE IF EXISTS public.image_data;

CREATE TABLE IF NOT EXISTS public.image_data
(
    image_id bigserial NOT NULL,
    image_name character varying COLLATE pg_catalog."default" NOT NULL,
    image_url character varying COLLATE pg_catalog."default" NOT NULL,
    algorithm character varying COLLATE pg_catalog."default" NOT NULL,
    threshold integer NOT NULL,
    upload_time timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "PK_image_data__image_id" PRIMARY KEY (image_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.image_data
    OWNER to admin;