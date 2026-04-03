-- ============================================================
-- Seed Data — Run AFTER schema.sql
-- Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- Stationary item names
do $$
declare
  depts text[] := array['CIV','EEE','MEC','ECE','CSE','CAI','CSM','CSE DS','CS','IT'];
  items text[] := array[
    'A/4 PAPER (70 GSM)','A/4COLOURPAPER(500P)','BELL CLIPS COLOUR','BELL CLIPS SMALL',
    'BOX FILES BIG','BOX FILES SMALL','C D MARKERS','CUTTERS','TIGER D/C PAPER','DUSTERS',
    'DUSTLESS CHALKPIECES WHITE','DUSTLESS COLOUR CHALK','ERASERS','FEVICOL 200GMS',
    'FOLDERS F.S','FOLDERS A 4','FOLDERS P.P. A/4(150 M.C.)','GUM STICKS MEDIUM',
    'GUMS 700ML CAMEL','GUMS DAYTONE','HIGHLITER PENS','L FOLDERS','LONG BOOKS (100P)A.P',
    'LONG BOOKS 160P. A.P','LONG NOTE BOOK RULED(BIND)NO.5','LONG NOTE BOOK RULED(BIND)NO.2',
    'LONG NOTE BOOK RULED(BIND)NO.3','LONG NOTE BOOK RULED(BIND)NO.4','MAHABAR 380P.BOOKS',
    'NOTICE BOARD PINS','PACKING WIRE','PENCILS','PENS (D.F.)','PENS (D.F.) BLACK',
    'PENS (D.F.) BLUE','PENS (D.F.) RED','PP COVERS','PUNCHING MACHINE BIG',
    'PUNCHING MACHINE DOUBLE HOLE','PVC FILES','RUBBER BANDS (500 GMS) SPL','SCISSORS BIG',
    'SHARPNER','SHORT BOOKS','SKETCH PENS SETS(BIG)','SPONZE DUMPERS','STAMP PAD INKS SMALL',
    'STAMP PADS MEDIUM','STAPPLER PINS 24/6','STAPPLER PINS NO 10','STAPPLERS HP 45',
    'STAPPLERS NO 10','STEEL SCALE LONG (METEL)','STICK FILES A4','SKETCH PEN PKS',
    'TAGS 8RL (BUNDELS)','TAPES BIG (BRN&TRN) 200 M','TAPES BIG(BROWN)',
    'THREAD (5PLY)(COTTON) (NO 2 SPL)','WHITE FLUID(CORRECTION PEN)','OTHERS'
  ];
  dept text;
  item text;
  qty  int;
begin
  foreach dept in array depts loop
    foreach item in array items loop
      qty := 50 + floor(random() * 450)::int;
      insert into public.assets (department, item_name, quantity)
      values (dept, item, qty)
      on conflict (department, item_name) do nothing;
    end loop;
  end loop;
end $$;

-- Sample indent requests
insert into public.indent_requests (indent_no, department, ordered_by, items, status) values
(
  'IND-SEED-001', 'CSE', 'Head of Dept',
  '[{"item":"A/4 PAPER (70 GSM)","quantity":"5"},{"item":"LONG BOOKS (100P)A.P","quantity":"20"}]',
  'Pending'
),
(
  'IND-SEED-002', 'EEE', 'Lab Incharge',
  '[{"item":"PENS (D.F.) BLUE","quantity":"10","approvedQty":"10","itemStatus":"Approved"}]',
  'Solved'
);

-- Sample item requests
insert into public.item_requests (department, item, quantity, status) values
('CSE', 'PENS (D.F.) BLUE', 10, 'Pending'),
('CIV', 'A/4 PAPER (70 GSM)', 5, 'Approved'),
('CSE', 'STAPPLERS HP 45', 1, 'Rejected');
