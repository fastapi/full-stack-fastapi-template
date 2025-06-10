-- Create projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planning',
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    manager_id UUID REFERENCES auth.users(id),
    branch_id UUID REFERENCES branches(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('planning', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

-- Create project_documents table
CREATE TABLE project_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_by UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create project_members table
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

-- Create project_tasks table
CREATE TABLE project_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'todo',
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
    assigned_to UUID REFERENCES auth.users(id),
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('todo', 'in_progress', 'review', 'done')),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

-- Create indexes
CREATE INDEX idx_projects_manager ON projects(manager_id);
CREATE INDEX idx_projects_branch ON projects(branch_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_project_documents_project ON project_documents(project_id);
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);
CREATE INDEX idx_project_tasks_project ON project_tasks(project_id);
CREATE INDEX idx_project_tasks_assigned ON project_tasks(assigned_to);
CREATE INDEX idx_project_tasks_status ON project_tasks(status);

-- Enable Row Level Security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_tasks ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view projects they are members of"
    ON projects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM project_members
            WHERE project_id = projects.id
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Managers can view all projects"
    ON projects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_roles
            WHERE user_id = auth.uid()
            AND role IN ('ceo', 'manager')
        )
    );

CREATE POLICY "Project members can view documents"
    ON project_documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM project_members
            WHERE project_id = project_documents.project_id
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Project members can view tasks"
    ON project_tasks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM project_members
            WHERE project_id = project_tasks.project_id
            AND user_id = auth.uid()
        )
    );

-- Create triggers
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_project_documents_updated_at
    BEFORE UPDATE ON project_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_project_tasks_updated_at
    BEFORE UPDATE ON project_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at(); 