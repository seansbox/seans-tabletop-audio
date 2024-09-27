def render_audio_list(audio_list):
    html = ""
    for entry in audio_list:
        html += render_audio_entry(**entry)
    return html


def render_audio_entry(title, image, type, flavor, tags, num, file, color="#FFFFFF"):
    return f"""
    <a href="#" onclick='return playMusic("{title.replace("'", "&apos;")}")' class="list-group-item list-group-item-action p-0" style="line-height: 97%; font-size: 85%; overflow: hidden; height: 50px">
        <img class="mediaImage float-left mx-1" src="{image}" style="width: 75px; height: 50px"/>
        <div class="pt-1 pr-1">
            <div class="text-nowrap">
                <b style="color: {color}">{title}</b>
                <span class="badge badge-dark" style="font-weight: normal;">{type}</span>
            </div>
            <span class="text-muted" style="font-size: 90%;">{flavor}</span>
            <span style="display:none">{', '.join(tags)}</span>
        </div>
    </a>"""


# Combine the components to render the full page
def render_html(title, audio_list):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <meta name="application-name" content="{ title }"/>
    <title>{ title }</title>

    <link rel="stylesheet" href="public/ttf/fira-sans-condensed.css">
    <link rel="stylesheet" href="public/ttf/nerd-font.css">
    <link rel="stylesheet" href="public/css/toggle-bootstrap.min.css">
    <link rel="stylesheet" href="public/css/toggle-bootstrap-dark.min.css">
    <link rel="stylesheet" href="public/css/toggle-bootstrap-print.min.css">
    <style>
        body.bootstrap, body.bootstrap-dark {{
            font-family: 'Fira Sans Condensed', sans-serif;
        }}
    </style>

    <link rel="shortcut icon" href="public/ico/favicon.ico">
    <link rel="icon" sizes="32x32" href="public/ico/favicon-32x32.png" />
    <link rel="icon" sizes="16x16" href="public/ico/favicon-16x16.png" />
    <link rel="apple-touch-icon-precomposed" sizes="57x57" href="public/ico/apple-touch-icon-57x57.png" />
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="public/ico/apple-touch-icon-72x72.png" />
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="public/ico/apple-touch-icon-114x114.png" />
    <link rel="apple-touch-icon-precomposed" sizes="120x120" href="public/ico/apple-touch-icon-120x120.png" />
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="public/ico/apple-touch-icon-144x144.png" />
    <link rel="apple-touch-icon-precomposed" sizes="152x152" href="public/ico/apple-touch-icon-152x152.png" />
    <meta name="msapplication-TileColor" content="#F44336" />
    <meta name="msapplication-TileImage" content="public/ico/mstile-144x144.png" />
</head>
<body class="bootstrap-dark">
    <nav class="navbar fixed-top navbar-dark bg-dark px-2">
        <form class="form-inline">
            <input class="form-control custom-select-sm" style="width: 100px;" type="text" id="mediaInput" onkeyup="filterMusic()" placeholder="Filter...">
            <button class="btn btn-secondary btn-sm ml-2" id="clearButton" onclick="return clearFilter()"><span class="nf nf-md-eraser"></span></button>
            <button class="btn btn-secondary btn-sm ml-2" id="combatButton" onclick="return combatFilter()"><span class="nf nf-md-sword_cross"></span></button>
            <button class="btn btn-secondary btn-sm ml-2" id="stopButton" style="display: none" onclick="return stopMusic()">⏯️</button>
        </form>
    </nav>

    <audio loop id="mediaPlayer" style="display: hidden">
        <source src="" type="audio/mpeg">
    </audio>

    <div id="audio-list" class="list-group" style="padding-top: 47px;">
        <script id="audio-template" type="text/x-handlebars-template">
            {render_audio_list(audio_list)}
        </script>
    </div>

    <script src="public/js/manifest.js"></script>
    <script src="public/js/script.js"></script>

    <script src="public/js/jquery.min.js"></script>
    <script src="public/js/bootstrap.bundle.min.js"></script>
    <script src="public/js/handlebars.min.js"></script>

</body>
</html>
"""
