#! /usr/bin/env bash

set -e
set -x

# Prestart checks
# Database migrations are managed by Supabase CLI (supabase db push)
# No local database or initial data seeding needed
echo "Prestart complete — no migrations required (Supabase manages schema)"
