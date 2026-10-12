import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "zhiyuan.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  short_name TEXT,
  org_type TEXT,
  role_note TEXT,
  plate TEXT,
  sort_order INTEGER
);
CREATE TABLE IF NOT EXISTS data_standards (
  code TEXT PRIMARY KEY,
  domain_code TEXT,
  domain_name TEXT,
  category2 TEXT,
  category3 TEXT,
  name TEXT,
  form TEXT,
  asset_class TEXT,
  meaning TEXT,
  reference_form TEXT,
  constraints TEXT,
  basis TEXT,
  positive_example TEXT,
  negative_example TEXT,
  sensitivity TEXT,
  related_rules TEXT
);
CREATE TABLE IF NOT EXISTS algorithms (
  code TEXT PRIMARY KEY,
  domain TEXT,
  subcategory TEXT,
  algo_type TEXT,
  name TEXT,
  scenario TEXT,
  data_needs TEXT,
  method TEXT,
  judgment TEXT,
  output_template TEXT,
  related_rules TEXT
);
CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  kind TEXT,
  code TEXT,
  name TEXT,
  plate TEXT,
  shape TEXT,
  status TEXT,
  maturity TEXT,
  summary TEXT,
  owner_org TEXT,
  maintainer TEXT,
  applicable TEXT,
  period TEXT,
  version TEXT,
  source_doc TEXT,
  source_locator TEXT,
  body_json TEXT
);
CREATE TABLE IF NOT EXISTS objects (
  id TEXT PRIMARY KEY,
  obj_type TEXT,
  name TEXT,
  summary TEXT,
  org_id TEXT,
  body_json TEXT
);
CREATE TABLE IF NOT EXISTS relations (
  id TEXT PRIMARY KEY,
  from_kind TEXT,
  from_id TEXT,
  to_kind TEXT,
  to_id TEXT,
  rel_type TEXT,
  period TEXT,
  condition TEXT,
  confirm_status TEXT,
  evidence TEXT
);
CREATE TABLE IF NOT EXISTS materials (
  id TEXT PRIMARY KEY,
  task_id TEXT,
  title TEXT,
  doc_type TEXT,
  doc_no TEXT,
  body TEXT
);
CREATE TABLE IF NOT EXISTS spans (
  id TEXT PRIMARY KEY,
  material_id TEXT,
  para_index INTEGER,
  text TEXT,
  tag TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  title TEXT,
  theme TEXT,
  status TEXT,
  expected TEXT,
  org_scope TEXT,
  summary TEXT,
  updated_note TEXT
);
CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY,
  task_id TEXT,
  material_id TEXT,
  kind TEXT,
  title TEXT,
  status TEXT,
  origin TEXT,
  confidence TEXT,
  span_ids TEXT,
  summary TEXT,
  body_json TEXT,
  abandon_reason TEXT,
  questions_json TEXT,
  asset_id TEXT
);
CREATE TABLE IF NOT EXISTS algo_trials (
  algo_code TEXT PRIMARY KEY,
  title TEXT,
  summary TEXT,
  rows_json TEXT,
  missing TEXT,
  other_explanations TEXT
);
CREATE TABLE IF NOT EXISTS versions (
  id TEXT PRIMARY KEY,
  asset_id TEXT,
  version TEXT,
  note TEXT,
  snapshot_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_std_domain ON data_standards(domain_code);
CREATE INDEX IF NOT EXISTS idx_std_name ON data_standards(name);
CREATE INDEX IF NOT EXISTS idx_algo_domain ON algorithms(domain);
CREATE INDEX IF NOT EXISTS idx_rel_from ON relations(from_kind, from_id);
CREATE INDEX IF NOT EXISTS idx_rel_to ON relations(to_kind, to_id);
"""


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def dumps(value):
    return json.dumps(value, ensure_ascii=False)


def loads(value, default=None):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def env_path():
    return ROOT.parent / ".env"


def load_env():
    path = env_path()
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())
