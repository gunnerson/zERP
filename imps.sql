--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3 (Ubuntu 12.3-1.pgdg18.04+1)
-- Dumped by pg_dump version 12.3 (Ubuntu 12.3-1.pgdg18.04+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: equip_imprint; Type: TABLE; Schema: public; Owner: db_user
--

CREATE TABLE public.equip_imprint (
    id integer NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    press_id integer
);


ALTER TABLE public.equip_imprint OWNER TO db_user;

--
-- Name: equip_imprint_id_seq; Type: SEQUENCE; Schema: public; Owner: db_user
--

CREATE SEQUENCE public.equip_imprint_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equip_imprint_id_seq OWNER TO db_user;

--
-- Name: equip_imprint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: db_user
--

ALTER SEQUENCE public.equip_imprint_id_seq OWNED BY public.equip_imprint.id;


--
-- Name: equip_imprint id; Type: DEFAULT; Schema: public; Owner: db_user
--

ALTER TABLE ONLY public.equip_imprint ALTER COLUMN id SET DEFAULT nextval('public.equip_imprint_id_seq'::regclass);


--
-- Data for Name: equip_imprint; Type: TABLE DATA; Schema: public; Owner: db_user
--

COPY public.equip_imprint (id, x, y, width, height, press_id) FROM stdin;
1	0	0	13	13	42
2	19	0	13	13	43
3	0	26	13	13	44
4	0	53	13	13	129
5	0	77	13	13	71
6	0	101	13	13	24
7	0	127	13	13	128
8	0	151	13	13	127
9	0	175	13	13	133
10	0	198	13	13	132
11	53	159	13	13	126
12	53	180	13	13	130
13	53	198	13	13	131
14	82	66	13	13	29
15	95	48	13	13	125
16	114	48	13	13	124
17	132	61	13	13	28
18	132	79	13	13	27
19	132	98	13	13	26
20	132	116	13	13	25
21	132	204	13	13	88
22	159	204	13	13	89
23	159	204	13	13	89
24	172	32	13	13	37
25	172	53	13	13	83
26	172	74	13	13	82
27	172	95	13	13	67
28	172	116	13	13	69
29	198	159	13	13	136
30	198	177	13	13	45
31	198	196	13	13	86
32	198	214	13	13	123
33	238	196	13	13	135
34	238	177	13	13	134
35	238	159	13	13	11
36	238	116	13	13	30
37	265	0	13	13	71
38	283	0	13	13	72
39	198	0	13	13	75
40	198	19	13	11	78
41	198	32	13	11	77
42	198	48	13	11	53
43	198	61	13	11	52
44	246	21	13	11	22
45	246	34	13	11	23
46	238	58	13	11	17
47	238	71	13	11	18
48	238	87	13	11	85
49	238	101	13	11	84
50	198	77	13	11	81
51	198	90	13	11	80
52	198	106	13	11	41
53	198	119	13	11	40
\.


--
-- Name: equip_imprint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: db_user
--

SELECT pg_catalog.setval('public.equip_imprint_id_seq', 53, true);


--
-- Name: equip_imprint equip_imprint_pkey; Type: CONSTRAINT; Schema: public; Owner: db_user
--

ALTER TABLE ONLY public.equip_imprint
    ADD CONSTRAINT equip_imprint_pkey PRIMARY KEY (id);


--
-- Name: equip_imprint_press_id_7585c2b1; Type: INDEX; Schema: public; Owner: db_user
--

CREATE INDEX equip_imprint_press_id_7585c2b1 ON public.equip_imprint USING btree (press_id);


--
-- Name: equip_imprint equip_imprint_press_id_7585c2b1_fk_equip_press_id; Type: FK CONSTRAINT; Schema: public; Owner: db_user
--

ALTER TABLE ONLY public.equip_imprint
    ADD CONSTRAINT equip_imprint_press_id_7585c2b1_fk_equip_press_id FOREIGN KEY (press_id) REFERENCES public.equip_press(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

