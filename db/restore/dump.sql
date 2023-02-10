--
-- PostgreSQL database dump
--

-- Dumped from database version 13.0
-- Dumped by pg_dump version 13.5 (Ubuntu 13.5-0ubuntu0.21.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auth; Type: DATABASE; Schema: -; Owner: app
--

--CREATE DATABASE auth WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';

CREATE SCHEMA IF NOT EXISTS content;

ALTER DATABASE auth OWNER TO app;

\connect auth

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: content; Type: SCHEMA; Schema: -; Owner: app
--


ALTER SCHEMA content OWNER TO app;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_role; Type: TABLE; Schema: content; Owner: app
--

CREATE TABLE content.auth_role (
    id uuid NOT NULL,
    name text NOT NULL
);


ALTER TABLE content.auth_role OWNER TO app;

--
-- Name: auth_users; Type: TABLE; Schema: content; Owner: app
--

CREATE TABLE content.auth_users (
    id uuid NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    role_id uuid NOT NULL
);


ALTER TABLE content.auth_users OWNER TO app;

--
-- Name: auth_users_log; Type: TABLE; Schema: content; Owner: app
--

CREATE TABLE content.auth_users_log (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    login_time timestamp with time zone DEFAULT now() NOT NULL,
    user_agent text
);


ALTER TABLE content.auth_users_log OWNER TO app;

--
-- Name: auth_users_role; Type: TABLE; Schema: content; Owner: app
--

CREATE TABLE content.auth_users_role (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    role_id uuid NOT NULL
);


ALTER TABLE content.auth_users_role OWNER TO app;

--
-- Data for Name: auth_role; Type: TABLE DATA; Schema: content; Owner: app
--

COPY content.auth_role (id, name) FROM stdin;
bc07dcbf-df6a-4412-9c37-33df3fad0ecd	admin
\.


--
-- Data for Name: auth_users; Type: TABLE DATA; Schema: content; Owner: app
--

COPY content.auth_users (id, login, password, role_id) FROM stdin;
\.


--
-- Data for Name: auth_users_log; Type: TABLE DATA; Schema: content; Owner: app
--

COPY content.auth_users_log (id, user_id, login_time, user_agent) FROM stdin;
\.


--
-- Data for Name: auth_users_role; Type: TABLE DATA; Schema: content; Owner: app
--

COPY content.auth_users_role (id, user_id, role_id) FROM stdin;
\.


--
-- Name: auth_role auth_role_pk; Type: CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_role
    ADD CONSTRAINT auth_role_pk PRIMARY KEY (id);


--
-- Name: auth_users_log auth_users_log_pk; Type: CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users_log
    ADD CONSTRAINT auth_users_log_pk PRIMARY KEY (id);


--
-- Name: auth_users auth_users_pk; Type: CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users
    ADD CONSTRAINT auth_users_pk PRIMARY KEY (id);


--
-- Name: auth_users_role auth_users_role_pk; Type: CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users_role
    ADD CONSTRAINT auth_users_role_pk PRIMARY KEY (id);


--
-- Name: auth_role_id_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_role_id_uindex ON content.auth_role USING btree (id);


--
-- Name: auth_role_name_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_role_name_uindex ON content.auth_role USING btree (name);


--
-- Name: auth_users_id_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_users_id_uindex ON content.auth_users USING btree (id);


--
-- Name: auth_users_log_id_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_users_log_id_uindex ON content.auth_users_log USING btree (id);


--
-- Name: auth_users_log_user_id_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_users_log_user_id_uindex ON content.auth_users_log USING btree (user_id);


--
-- Name: auth_users_login_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_users_login_uindex ON content.auth_users USING btree (login);


--
-- Name: auth_users_role_id_uindex; Type: INDEX; Schema: content; Owner: app
--

CREATE UNIQUE INDEX auth_users_role_id_uindex ON content.auth_users USING btree (role_id);


--
-- Name: auth_users_log auth_users_log_auth_users_id_fk; Type: FK CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users_log
    ADD CONSTRAINT auth_users_log_auth_users_id_fk FOREIGN KEY (user_id) REFERENCES content.auth_users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: auth_users_role auth_users_role_auth_role_id_fk; Type: FK CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users_role
    ADD CONSTRAINT auth_users_role_auth_role_id_fk FOREIGN KEY (role_id) REFERENCES content.auth_role(id);


--
-- Name: auth_users_role auth_users_role_auth_users_id_fk; Type: FK CONSTRAINT; Schema: content; Owner: app
--

ALTER TABLE ONLY content.auth_users_role
    ADD CONSTRAINT auth_users_role_auth_users_id_fk FOREIGN KEY (user_id) REFERENCES content.auth_users(id);


--
-- PostgreSQL database dump complete
--

