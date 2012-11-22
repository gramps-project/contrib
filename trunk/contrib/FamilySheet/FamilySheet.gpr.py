register(REPORT,
    id   = 'FamilySheet',
    name = _('Family Sheet'),
    description = _("Produces a family sheet showing full information "
                    "about a person and his/her partners and children."),
    version = '3.4.15',
    gramps_target_version = '4.0',
    status = STABLE, # not yet tested with python 3
    fname = 'FamilySheet.py',
    authors = ["Reinhard Mueller"],
    authors_email = ["reinhard.mueller@igal.at"],
    category = CATEGORY_TEXT,
    reportclass = 'FamilySheet',
    optionclass = 'FamilySheetOptions',
    report_modes = [REPORT_MODE_GUI],
    require_active = True
    )
