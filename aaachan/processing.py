from flask import Markup

class Processing():
    @staticmethod
    def text_to_html(content: str, current_id: str) -> (str, list):
        html_str = ''
        quote_list = []
        for line in content.splitlines():
            fline = ''
            first = True
            first_is_quote = False

            for word in line.split(' '):
                if word.startswith('>>'):
                    maybe_quote = word[2:]
                    if maybe_quote.isdigit():
                        # Quote detected, link it and add to quote_list
                        fline += '<a href="#post_'+maybe_quote+\
                                '">&#62;&#62;'+maybe_quote+'</a> '
                        quote_list.append({
                            'target' : maybe_quote,
                            'by' : current_id
                        })
                        if first:
                            first_is_quote = True
                    else:
                        fline += word + ' '
                else:
                    fline += word + ' '

                if first:
                    first = False

            if fline.startswith('>') and not first_is_quote:
                # Might be a quote
                html_str += '<span class="quotetext">'+fline+'</span>'
            else:
                html_str += fline
            html_str += '<br>'
        return (Markup(html_str), quote_list)

    @staticmethod
    def allowed_content(content: str) -> bool:
        return (not '<script>' in content)

    @staticmethod
    def limiter(content: str, limit: int) -> str:
        if len(content) > limit:
            return content[0:limit]+"..."
        else:
            return content

