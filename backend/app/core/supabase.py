from supabase import create_client, Client
from ..core.config import settings

def get_supabase_client() -> Client:
    """
    Obtiene el cliente de Supabase configurado
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )

# Configuración de las tablas en Supabase
SUPABASE_TABLES = {
    "properties": """
        create table if not exists properties (
            id uuid default uuid_generate_v4() primary key,
            title text not null,
            description text,
            price decimal not null,
            property_type text not null,
            status text not null,
            address text not null,
            city text not null,
            state text not null,
            zip_code text not null,
            bedrooms integer,
            bathrooms integer,
            area decimal not null,
            features text[] default '{}',
            images text[] default '{}',
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
            owner_id uuid references auth.users(id) not null
        );
    """,
    "transactions": """
        create table if not exists transactions (
            id uuid default uuid_generate_v4() primary key,
            property_id uuid references properties(id) not null,
            buyer_id uuid references auth.users(id) not null,
            seller_id uuid references auth.users(id) not null,
            amount decimal not null,
            transaction_type text not null,
            status text not null,
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null
        );
    """,
    "credits": """
        create table if not exists credits (
            id uuid default uuid_generate_v4() primary key,
            user_id uuid references auth.users(id) not null,
            property_id uuid references properties(id) not null,
            amount decimal not null,
            interest_rate decimal not null,
            term_months integer not null,
            status text not null,
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null
        );
    """,
    "appraisals": """
        create table if not exists appraisals (
            id uuid default uuid_generate_v4() primary key,
            property_id uuid references properties(id) not null,
            appraiser_id uuid references auth.users(id) not null,
            value decimal not null,
            report_url text not null,
            status text not null,
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null
        );
    """,
    "management_contracts": """
        create table if not exists management_contracts (
            id uuid default uuid_generate_v4() primary key,
            property_id uuid references properties(id) not null,
            owner_id uuid references auth.users(id) not null,
            manager_id uuid references auth.users(id) not null,
            start_date timestamp with time zone not null,
            end_date timestamp with time zone not null,
            fee_percentage decimal not null,
            status text not null,
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null
        );
    """,
    "advisory_sessions": """
        create table if not exists advisory_sessions (
            id uuid default uuid_generate_v4() primary key,
            client_id uuid references auth.users(id) not null,
            advisor_id uuid references auth.users(id) not null,
            topic text not null,
            notes text,
            status text not null,
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
            updated_at timestamp with time zone default timezone('utc'::text, now()) not null
        );
    """
}

# Políticas de seguridad RLS (Row Level Security)
SUPABASE_POLICIES = {
    "properties": """
        -- Habilitar RLS
        alter table properties enable row level security;

        -- Política para lectura pública
        create policy "Properties are viewable by everyone"
        on properties for select
        using (true);

        -- Política para inserción (solo usuarios autenticados)
        create policy "Users can insert their own properties"
        on properties for insert
        with check (auth.uid() = owner_id);

        -- Política para actualización (solo propietarios)
        create policy "Users can update their own properties"
        on properties for update
        using (auth.uid() = owner_id);

        -- Política para eliminación (solo propietarios)
        create policy "Users can delete their own properties"
        on properties for delete
        using (auth.uid() = owner_id);
    """,
    "transactions": """
        alter table transactions enable row level security;

        create policy "Transactions are viewable by participants"
        on transactions for select
        using (auth.uid() = buyer_id or auth.uid() = seller_id);

        create policy "Users can create transactions"
        on transactions for insert
        with check (auth.uid() = buyer_id);
    """,
    "credits": """
        alter table credits enable row level security;

        create policy "Credits are viewable by owner"
        on credits for select
        using (auth.uid() = user_id);

        create policy "Users can create their own credits"
        on credits for insert
        with check (auth.uid() = user_id);
    """,
    "appraisals": """
        alter table appraisals enable row level security;

        create policy "Appraisals are viewable by property owner and appraiser"
        on appraisals for select
        using (
            auth.uid() = appraiser_id or
            exists (
                select 1 from properties
                where properties.id = appraisals.property_id
                and properties.owner_id = auth.uid()
            )
        );
    """,
    "management_contracts": """
        alter table management_contracts enable row level security;

        create policy "Contracts are viewable by owner and manager"
        on management_contracts for select
        using (auth.uid() = owner_id or auth.uid() = manager_id);
    """,
    "advisory_sessions": """
        alter table advisory_sessions enable row level security;

        create policy "Sessions are viewable by client and advisor"
        on advisory_sessions for select
        using (auth.uid() = client_id or auth.uid() = advisor_id);
    """
} 