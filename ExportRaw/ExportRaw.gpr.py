register(EXPORT,
         id    = 'Raw Export',
         name  = _('Raw Export'),
         description =  _('This is a raw python object dump'),
         version = '1.0.39',
         gramps_target_version = "5.2",
         status = STABLE,
         audience = DEVELOPER,
         fname = 'ExportRaw.py',
         export_function = 'exportData',
         export_options = 'WriterOptionBox',
         export_options_title = _('Raw options'),
         extension = "raw"
         )
