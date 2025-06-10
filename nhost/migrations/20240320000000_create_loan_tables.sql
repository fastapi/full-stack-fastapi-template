-- Create mortgage_loans table
CREATE TABLE mortgage_loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    term_years INTEGER NOT NULL,
    ltv_ratio DECIMAL(5,2) NOT NULL,
    monthly_payment DECIMAL(15,2) NOT NULL,
    insurance_required BOOLEAN DEFAULT false,
    insurance_provider VARCHAR(255),
    insurance_policy_number VARCHAR(255),
    insurance_coverage DECIMAL(15,2),
    appraisal_value DECIMAL(15,2) NOT NULL,
    appraisal_date DATE,
    appraisal_company VARCHAR(255),
    legal_documents JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES auth.users(id),
    approved_by UUID REFERENCES auth.users(id),
    approval_date TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 'closed')),
    CONSTRAINT valid_term_years CHECK (term_years BETWEEN 1 AND 30),
    CONSTRAINT valid_interest_rate CHECK (interest_rate BETWEEN 0 AND 100),
    CONSTRAINT valid_ltv_ratio CHECK (ltv_ratio BETWEEN 0 AND 100)
);

-- Create investment_loans table
CREATE TABLE investment_loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    term_years INTEGER NOT NULL,
    expected_roi DECIMAL(5,2) NOT NULL,
    business_plan TEXT,
    collateral_type VARCHAR(50),
    collateral_value DECIMAL(15,2),
    collateral_documents JSONB,
    risk_assessment JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES auth.users(id),
    approved_by UUID REFERENCES auth.users(id),
    approval_date TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 'closed')),
    CONSTRAINT valid_term_years CHECK (term_years BETWEEN 1 AND 30),
    CONSTRAINT valid_interest_rate CHECK (interest_rate BETWEEN 0 AND 100),
    CONSTRAINT valid_expected_roi CHECK (expected_roi BETWEEN 0 AND 100)
);

-- Create indexes
CREATE INDEX idx_mortgage_loans_property_id ON mortgage_loans(property_id);
CREATE INDEX idx_mortgage_loans_created_by ON mortgage_loans(created_by);
CREATE INDEX idx_mortgage_loans_status ON mortgage_loans(status);

CREATE INDEX idx_investment_loans_project_id ON investment_loans(project_id);
CREATE INDEX idx_investment_loans_created_by ON investment_loans(created_by);
CREATE INDEX idx_investment_loans_status ON investment_loans(status);

-- Create RLS policies
ALTER TABLE mortgage_loans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own mortgage loans"
    ON mortgage_loans FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Managers can view all mortgage loans"
    ON mortgage_loans FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    );

CREATE POLICY "Users can create mortgage loans"
    ON mortgage_loans FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager', 'supervisor')
        )
    );

CREATE POLICY "Managers can update mortgage loans"
    ON mortgage_loans FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    );

ALTER TABLE investment_loans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own investment loans"
    ON investment_loans FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Managers can view all investment loans"
    ON investment_loans FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    );

CREATE POLICY "Users can create investment loans"
    ON investment_loans FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    );

CREATE POLICY "Managers can update investment loans"
    ON investment_loans FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    ); 