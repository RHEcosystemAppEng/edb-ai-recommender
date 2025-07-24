{{/*
Generated helper file for llama-wrapper chart
*/}}

{{- define "llama-wrapper.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{- define "llama-wrapper.fullname" -}}
{{- printf "%s-%s" (include "llama-wrapper.name" .) .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "llama-wrapper.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "llama-wrapper.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "llama-wrapper.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "llama-wrapper.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
