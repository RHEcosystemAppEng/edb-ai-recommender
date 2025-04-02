{{- define "ai-recommender.primary-labels" }}
app.kubernetes.io/name: {{.Release.Name}}
app.kubernetes.io/instance: {{.Release.Name}}
app.kubernetes.io/managed-by: Helm
helm.sh/chart: {{.Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}