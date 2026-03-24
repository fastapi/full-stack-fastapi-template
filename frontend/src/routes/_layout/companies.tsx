import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { CompaniesService, type CompanyCreate } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  cnpj: z.string().min(1, { message: "CNPJ é obrigatório" }),
  razao_social: z.string().min(1, { message: "Razão Social é obrigatória" }),
  representante_legal: z
    .string()
    .min(1, { message: "Representante Legal é obrigatório" }),
  data_abertura: z
    .string()
    .min(1, { message: "Data de Abertura é obrigatória" }),
  nome_fantasia: z.string().min(1, { message: "Nome Fantasia é obrigatório" }),
  porte: z.string().min(1, { message: "Porte é obrigatório" }),
  atividade_economica_principal: z
    .string()
    .min(1, { message: "Atividade Econômica Principal é obrigatória" }),
  atividade_economica_secundaria: z
    .string()
    .min(1, { message: "Atividade Econômica Secundária é obrigatória" }),
  natureza_juridica: z
    .string()
    .min(1, { message: "Natureza Jurídica é obrigatória" }),
  logradouro: z.string().min(1, { message: "Logradouro é obrigatório" }),
  numero: z.string().min(1, { message: "Número é obrigatório" }),
  complemento: z.string().min(1, { message: "Complemento é obrigatório" }),
  cep: z.string().min(1, { message: "CEP é obrigatório" }),
  bairro: z.string().min(1, { message: "Bairro é obrigatório" }),
  municipio: z.string().min(1, { message: "Município é obrigatório" }),
  uf: z.string().min(1, { message: "UF é obrigatória" }),
  endereco_eletronico: z
    .string()
    .min(1, { message: "Endereço Eletrônico é obrigatório" }),
  telefone_comercial: z
    .string()
    .min(1, { message: "Telefone Comercial é obrigatório" }),
  situacao_cadastral: z
    .string()
    .min(1, { message: "Situação Cadastral é obrigatória" }),
  data_situacao_cadastral: z
    .string()
    .min(1, { message: "Data Situação Cadastral é obrigatória" }),
  cpf_representante_legal: z
    .string()
    .min(1, { message: "CPF do Representante Legal é obrigatório" }),
  identidade_representante_legal: z
    .string()
    .min(1, { message: "Identidade do Representante Legal é obrigatória" }),
  logradouro_representante_legal: z
    .string()
    .min(1, { message: "Logradouro do Representante Legal é obrigatório" }),
  numero_representante_legal: z
    .string()
    .min(1, { message: "Número do Representante Legal é obrigatório" }),
  complemento_representante_legal: z
    .string()
    .min(1, { message: "Complemento do Representante Legal é obrigatório" }),
  cep_representante_legal: z
    .string()
    .min(1, { message: "CEP do Representante Legal é obrigatório" }),
  bairro_representante_legal: z
    .string()
    .min(1, { message: "Bairro do Representante Legal é obrigatório" }),
  municipio_representante_legal: z
    .string()
    .min(1, { message: "Município do Representante Legal é obrigatório" }),
  uf_representante_legal: z
    .string()
    .min(1, { message: "UF do Representante Legal é obrigatória" }),
  endereco_eletronico_representante_legal: z.string().min(1, {
    message: "Endereço Eletrônico do Representante Legal é obrigatório",
  }),
  telefones_representante_legal: z
    .string()
    .min(1, { message: "Telefones do Representante Legal é obrigatório" }),
  data_nascimento_representante_legal: z.string().min(1, {
    message: "Data de Nascimento do Representante Legal é obrigatória",
  }),
  banco_cc_cnpj: z
    .string()
    .min(1, { message: "Banco CC do CNPJ é obrigatório" }),
  agencia_cc_cnpj: z
    .string()
    .min(1, { message: "Agência CC do CNPJ é obrigatória" }),
})

type FormData = z.infer<typeof formSchema>

const defaultValues: FormData = {
  cnpj: "",
  razao_social: "",
  representante_legal: "",
  data_abertura: "",
  nome_fantasia: "",
  porte: "",
  atividade_economica_principal: "",
  atividade_economica_secundaria: "",
  natureza_juridica: "",
  logradouro: "",
  numero: "",
  complemento: "",
  cep: "",
  bairro: "",
  municipio: "",
  uf: "",
  endereco_eletronico: "",
  telefone_comercial: "",
  situacao_cadastral: "",
  data_situacao_cadastral: "",
  cpf_representante_legal: "",
  identidade_representante_legal: "",
  logradouro_representante_legal: "",
  numero_representante_legal: "",
  complemento_representante_legal: "",
  cep_representante_legal: "",
  bairro_representante_legal: "",
  municipio_representante_legal: "",
  uf_representante_legal: "",
  endereco_eletronico_representante_legal: "",
  telefones_representante_legal: "",
  data_nascimento_representante_legal: "",
  banco_cc_cnpj: "",
  agencia_cc_cnpj: "",
}

export const Route = createFileRoute("/_layout/companies")({
  component: Companies,
  head: () => ({
    meta: [
      {
        title: "Cadastro PJ - Controle de PJs",
      },
    ],
  }),
})

interface FieldConfig {
  name: keyof FormData
  label: string
  type: string
}

const dadosEmpresaFields: FieldConfig[] = [
  { name: "cnpj", label: "CNPJ", type: "text" },
  { name: "razao_social", label: "Razão Social", type: "text" },
  { name: "nome_fantasia", label: "Nome Fantasia", type: "text" },
  { name: "data_abertura", label: "Data de Abertura", type: "date" },
  { name: "porte", label: "Porte", type: "text" },
  {
    name: "atividade_economica_principal",
    label: "Atividade Econômica Principal",
    type: "text",
  },
  {
    name: "atividade_economica_secundaria",
    label: "Atividade Econômica Secundária",
    type: "text",
  },
  { name: "natureza_juridica", label: "Natureza Jurídica", type: "text" },
  { name: "situacao_cadastral", label: "Situação Cadastral", type: "text" },
  {
    name: "data_situacao_cadastral",
    label: "Data Situação Cadastral",
    type: "date",
  },
]

const enderecoEmpresaFields: FieldConfig[] = [
  { name: "logradouro", label: "Logradouro", type: "text" },
  { name: "numero", label: "Número", type: "text" },
  { name: "complemento", label: "Complemento", type: "text" },
  { name: "cep", label: "CEP", type: "text" },
  { name: "bairro", label: "Bairro", type: "text" },
  { name: "municipio", label: "Município", type: "text" },
  { name: "uf", label: "UF", type: "text" },
]

const contatoEmpresaFields: FieldConfig[] = [
  {
    name: "endereco_eletronico",
    label: "Endereço Eletrônico",
    type: "text",
  },
  { name: "telefone_comercial", label: "Telefone Comercial", type: "text" },
]

const dadosRepresentanteFields: FieldConfig[] = [
  {
    name: "representante_legal",
    label: "Representante Legal",
    type: "text",
  },
  {
    name: "cpf_representante_legal",
    label: "CPF Representante Legal",
    type: "text",
  },
  {
    name: "identidade_representante_legal",
    label: "Identidade Representante Legal",
    type: "text",
  },
  {
    name: "data_nascimento_representante_legal",
    label: "Data de Nascimento Representante Legal",
    type: "date",
  },
]

const enderecoRepresentanteFields: FieldConfig[] = [
  {
    name: "logradouro_representante_legal",
    label: "Logradouro Representante Legal",
    type: "text",
  },
  {
    name: "numero_representante_legal",
    label: "Número Representante Legal",
    type: "text",
  },
  {
    name: "complemento_representante_legal",
    label: "Complemento Representante Legal",
    type: "text",
  },
  {
    name: "cep_representante_legal",
    label: "CEP Representante Legal",
    type: "text",
  },
  {
    name: "bairro_representante_legal",
    label: "Bairro Representante Legal",
    type: "text",
  },
  {
    name: "municipio_representante_legal",
    label: "Município Representante Legal",
    type: "text",
  },
  {
    name: "uf_representante_legal",
    label: "UF Representante Legal",
    type: "text",
  },
]

const contatoRepresentanteFields: FieldConfig[] = [
  {
    name: "endereco_eletronico_representante_legal",
    label: "Endereço Eletrônico Representante Legal",
    type: "text",
  },
  {
    name: "telefones_representante_legal",
    label: "Telefones Representante Legal",
    type: "text",
  },
]

const dadosBancariosFields: FieldConfig[] = [
  { name: "banco_cc_cnpj", label: "Banco CC do CNPJ", type: "text" },
  { name: "agencia_cc_cnpj", label: "Agência CC do CNPJ", type: "text" },
]

function FieldGroup({
  fields,
  form,
}: {
  fields: FieldConfig[]
  form: ReturnType<typeof useForm<FormData>>
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {fields.map((fieldConfig) => (
        <FormField
          key={fieldConfig.name}
          control={form.control}
          name={fieldConfig.name}
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                {fieldConfig.label} <span className="text-destructive">*</span>
              </FormLabel>
              <FormControl>
                <Input
                  placeholder={fieldConfig.label}
                  type={fieldConfig.type}
                  {...field}
                  required
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      ))}
    </div>
  )
}

function Companies() {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues,
  })

  const mutation = useMutation({
    mutationFn: (data: CompanyCreate) =>
      CompaniesService.createCompanyRoute({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Cadastro recebido com sucesso!")
      form.reset()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Cadastro PJ</h1>
        <p className="text-muted-foreground">
          Preencha os dados básicos da Pessoa Jurídica para iniciar o processo
          de admissão.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Dados da Empresa</CardTitle>
              <CardDescription>
                Informações básicas da Pessoa Jurídica
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={dadosEmpresaFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Endereço da Empresa</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={enderecoEmpresaFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contato da Empresa</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={contatoEmpresaFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Dados do Representante Legal</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={dadosRepresentanteFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Endereço do Representante Legal</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={enderecoRepresentanteFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contato do Representante Legal</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={contatoRepresentanteFields} form={form} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Dados Bancários</CardTitle>
            </CardHeader>
            <CardContent>
              <FieldGroup fields={dadosBancariosFields} form={form} />
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => form.reset()}
              disabled={mutation.isPending}
            >
              Limpar
            </Button>
            <LoadingButton type="submit" loading={mutation.isPending}>
              Cadastrar
            </LoadingButton>
          </div>
        </form>
      </Form>
    </div>
  )
}
