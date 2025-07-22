<#
.SYNOPSIS
    Анализирует XML-файлы метаданных объекта 1С и генерирует "Контракт Модуля" для каждой его формы.

.DESCRIPTION
    Этот скрипт автоматизирует процесс документирования модулей форм в 1С.
    Он принимает на вход путь к XML-файлу объекта конфигурации (документа, справочника, обработки и т.д.),
    автоматически находит все связанные с ним формы, парсит их структуру и структуру самого объекта,
    а затем выводит в консоль отформатированный "Контракт Модуля" для каждой найденной формы.

    Контракт включает в себя:
    - Элементы управления формы (таблицы, поля, кнопки).
    - Реквизиты объекта.
    - Табличные части объекта и их колонки.

.PARAMETER ObjectXmlPath
    Обязательный параметр. Указывает путь к основному XML-файлу объекта конфигурации.
    Например, "C:\1C\src\Documents\РеализацияТоваровУслуг.xml".

.EXAMPLE
    PS C:\> .\Generate-ModuleContract.ps1 -ObjectXmlPath "C:\project\src\ExternalDataProcessors\МояОбработка.xml"

    Этот пример запустит анализ для внешней обработки "МояОбработка" и выведет контракты для всех ее форм.
#>

# PowerShell-скрипт для генерации "Контракта Модуля" на основе XML-файлов метаданных 1С.

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string]$ObjectXmlPath
)

# Функция для парсинга XML-файла объекта (документа, обработки и т.д.)
function ConvertFrom-ObjectXml {
    param (
        [string]$FilePath
    )

    try {
        [xml]$xml = Get-Content -Path $FilePath -Raw
        
        # Регистрация пространства имен для XPath
        $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace("mdclass", "http://v8.1c.ru/8.3/MDClasses")
        $ns.AddNamespace("core", "http://v8.1c.ru/8.1/data/core")

        # Формируем базовый путь, чтобы избежать выбора вложенных элементов (например, реквизитов из ТЧ)
        $basePath = "/mdclass:MetaDataObject/*[1]/mdclass:ChildObjects"

        # Находим все реквизиты, табличные части и формы
        $attributes = $xml.SelectNodes("$basePath/mdclass:Attribute", $ns)
        $tabularSections = $xml.SelectNodes("$basePath/mdclass:TabularSection", $ns)
        $forms = $xml.SelectNodes("$basePath/mdclass:Form", $ns)
        
        $result = @{
            Attributes      = @()
            TabularSections = @()
            Forms           = @()
        }

        # Обработка реквизитов
        foreach ($attr in $attributes) {
            $name = $attr.Properties.Name
            $type = ($attr.Properties.Type.SelectSingleNode("core:Type", $ns) | ForEach-Object { $_.InnerText }).Trim()
            if (-not $type) { $type = ($attr.Properties.Type.SelectSingleNode("core:Type", $ns) | ForEach-Object { $_.'#text' }).Trim() }
            if (-not $type) { $type = "Не определен" }
            $result.Attributes += @{ Name = $name; Type = $type }
        }

        # Обработка табличных частей
        foreach ($section in $tabularSections) {
            $sectionName = $section.Properties.Name
            $sectionData = @{ Name = $sectionName; Columns = @() }
            $columns = $section.SelectNodes("mdclass:ChildObjects/mdclass:Attribute", $ns)
            foreach ($col in $columns) {
                $colName = $col.Properties.Name
                $colType = ($col.Properties.Type.SelectSingleNode("core:Type", $ns) | ForEach-Object { $_.InnerText }).Trim()
                if (-not $colType) { $colType = ($col.Properties.Type.SelectSingleNode("core:Type", $ns) | ForEach-Object { $_.'#text' }).Trim() }
                if (-not $colType) { $colType = $col.Properties.Type.InnerText.Trim() }
                if (-not $colType) { $colType = "Не определен" }
                $sectionData.Columns += @{ Name = $colName; Type = $colType }
            }
            $result.TabularSections += $sectionData
        }
        
        # Обработка форм
        foreach ($form in $forms) {
            # Пытаемся получить имя из свойства, как в стандартных объектах
            $formName = $form.Properties.Name
            # Если не получилось, берем InnerText, как во внешних обработках
            if (-not $formName) {
                $formName = $form.InnerText.Trim()
            }
            
            if (-not [string]::IsNullOrWhiteSpace($formName)) {
                # Избегаем дубликатов, если оба метода что-то вернут
                if ($result.Forms -notcontains $formName) {
                    $result.Forms += $formName
                }
            }
        }

        return $result
    }
    catch {
        Write-Error "Ошибка при парсинге XML объекта: $_"
        return $null
    }
}

# Функция для парсинга XML-файла формы
function ConvertFrom-FormXml {
    param (
        [string]$FilePath
    )

    try {
        [xml]$xml = Get-Content -Path $FilePath -Raw
        $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace("logform", "http://v8.1c.ru/8.3/xcf/logform")

        $result = @{ Tables = @(); InputFields = @(); Buttons = @() }
        $elements = $xml.SelectNodes("//logform:*[self::logform:Table or self::logform:InputField or self::logform:Button]", $ns)
        
        foreach ($el in $elements) {
            switch ($el.LocalName) {
                "Table" { $result.Tables += $el.name }
                "InputField" { $result.InputFields += $el.name }
                "Button" { $result.Buttons += $el.name }
            }
        }
        return $result
    }
    catch {
        Write-Error "Ошибка при парсинге XML формы '$FilePath': $_"
        return $null
    }
}

# Функция для генерации итогового "Контракта Модуля"
function New-ModuleContract {
    param (
        [string]$FormName,
        [hashtable]$ObjectData,
        [hashtable]$FormData
    )

    $formElementTypeMap = @{
        "Table"      = "ТаблицаФормы"
        "InputField" = "ПолеФормы"
        "Button"     = "КнопкаФормы"
    }

    $contract = @"
// =======================================
// Контракт Модуля для формы: $FormName
// (сгенерирован автоматически)
// =======================================
//
// Тип модуля: Модуль формы (управляемая)
// Контекст выполнения: &НаКлиенте, &НаСервере, &НаСервереБезКонтекста
//
// --- Декларация ключевых типов данных ---
//
// --- Элементы формы (визуальные компоненты) ---
"@

    $FormData.Tables | ForEach-Object { $contract += "`n// Элементы.$_".PadRight(35) + "| $($formElementTypeMap['Table'])" }
    $FormData.InputFields | ForEach-Object { $contract += "`n// Элементы.$_".PadRight(35) + "| $($formElementTypeMap['InputField'])" }
    $FormData.Buttons | ForEach-Object { $contract += "`n// Элементы.$_".PadRight(35) + "| $($formElementTypeMap['Button'])" }

    if ($ObjectData.Attributes.Count -gt 0) {
        $contract += @"

// --- Реквизиты объекта ---
"@
        $ObjectData.Attributes | ForEach-Object {
            $type = $_.Type
            switch -Wildcard ($type) {
                'xs:boolean' { $type = 'Булево'; break }
                'xs:string' { $type = 'Строка'; break }
                'v8:StandardPeriod' { $type = 'СтандартныйПериод'; break }
                'cfg:CatalogRef*' { $type = $type.Replace('cfg:CatalogRef', 'СправочникСсылка'); break }
                'cfg:DocumentRef*' { $type = $type.Replace('cfg:DocumentRef', 'ДокументСсылка'); break }
                default { $type = $type.Replace("cfg:", "").Replace("v8:", "") } # Fallback
            }
            $contract += "`n//  ├─ $($_.Name)".PadRight(35) + "| $type"
        }
    }

    if ($ObjectData.TabularSections.Count -gt 0) {
        $contract += @"

// --- Табличные части объекта ---
"@
        foreach ($section in $ObjectData.TabularSections) {
            $contract += "`n// Объект.$($section.Name)".PadRight(35) + "| ДанныеФормыКоллекция"
            foreach ($column in $section.Columns) {
                $type = $column.Type
                switch -Wildcard ($type) {
                    'xs:boolean' { $type = 'Булево'; break }
                    'xs:string' { $type = 'Строка'; break }
                    'v8:StandardPeriod' { $type = 'СтандартныйПериод'; break }
                    'cfg:CatalogRef*' { $type = $type.Replace('cfg:CatalogRef', 'СправочникСсылка'); break }
                    'cfg:DocumentRef*' { $type = $type.Replace('cfg:DocumentRef', 'ДокументСсылка'); break }
                    default { $type = $type.Replace("cfg:", "").Replace("v8:", "").Replace("xs:", "") } # Fallback
                }
                $contract += "`n//  ├─ $($column.Name)".PadRight(35) + "| $type"
            }
        }
    }

    $contract += @"

// =======================================
"@
    return $contract
}

# --- Основная логика скрипта ---
$ObjectData = ConvertFrom-ObjectXml -FilePath $ObjectXmlPath

if ($ObjectData) {
    $ObjectFile = Get-Item -Path $ObjectXmlPath
    # Путь к каталогу, где лежат подкаталоги с формами (например, .../СозданиеОбработкиДляЗаполненияНовойГОВСтарыхДокументах/)
    $FormsBaseDir = Join-Path -Path $ObjectFile.DirectoryName -ChildPath $ObjectFile.BaseName
    
    if ($ObjectData.Forms.Count -eq 0) {
        Write-Warning "В файле объекта не найдено ни одной формы."
        return
    }

    Write-Host "Найдены формы: $($ObjectData.Forms -join ', ')" -ForegroundColor Green

    foreach ($formName in $ObjectData.Forms) {
        $formXmlPath = Join-Path -Path $FormsBaseDir -ChildPath "Forms\$formName\Ext\Form.xml"

        if (Test-Path $formXmlPath) {
            Write-Host "`n"
            Write-Host "--- ГЕНЕРАЦИЯ КОНТРАКТА ДЛЯ ФОРМЫ: $formName ---" -ForegroundColor Yellow
            
            $FormData = ConvertFrom-FormXml -FilePath $formXmlPath
            if ($FormData) {
                $ModuleContract = New-ModuleContract -FormName $formName -ObjectData $ObjectData -FormData $FormData
                Write-Host $ModuleContract
            }
        }
        else {
            Write-Warning "XML для формы '$formName' не найден. Ожидаемый путь: $formXmlPath"
        }
    }
} 