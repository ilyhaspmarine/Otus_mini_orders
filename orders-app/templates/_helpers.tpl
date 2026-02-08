{{/*
Expand the name of the chart.
*/}}
{{- define "orders-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "orders-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "orders-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "orders-app.labels" -}}
helm.sh/chart: {{ include "orders-app.chart" . }}
{{ include "orders-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "orders-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "orders-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "orders-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "orders-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Формирует имя сервиса PostgreSQL, используя Release.Name и postgresql.nameOverride
*/}}
{{- define "orders-app.dbhost" -}}
{{- $releaseName := .Release.Name -}}
{{- $nameOverride := .Values.postgresql.nameOverride -}}
{{- if $nameOverride -}}
{{- printf "%s-%s" $releaseName $nameOverride -}}
{{- else -}}
{{- printf "%s-%s" $releaseName "postgresql" -}} {{/* Значение по умолчанию, если nameOverride не задан */}}
{{- end -}}
{{- end }}

{{/*
Формирует имя configMap используя Release.Name и константу
*/}}
{{- define "orders-app.configMapName" -}}
{{- $releaseName := .Release.Name -}}
{{- printf "%s-%s" $releaseName "config" -}}
{{- end }}

{{/*
Формирует имя ingress используя Release.Name и константу
*/}}
{{- define "orders-app.ingressName" -}}
{{- $releaseName := .Release.Name -}}
{{- printf "%s-%s" $releaseName "ingress" -}}
{{- end }}

{{/*
Формирует имя service используя Release.Name и константу
*/}}
{{- define "orders-app.serviceName" -}}
{{- $releaseName := .Release.Name -}}
{{- printf "%s-%s" $releaseName "service" -}}
{{- end }}

{{/*
Формирует имя app используя Release.Name и константу
*/}}
{{- define "orders-app.appName" -}}
{{- $releaseName := .Release.Name -}}
{{- printf "%s-%s" $releaseName "app" -}}
{{- end }}

{{/*
Формирует имя serviceMonitor используя Release.Name и константу
*/}}
{{- define "orders-app.serviceMonitorName" -}}
{{- $releaseName := .Release.Name -}}
{{- printf "%s-%s" $releaseName "service-monitor" -}}
{{- end }}