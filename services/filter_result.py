import re
import os


def filter_code(html_content):
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # Use regular expression to extract content between triple single quotes
    matches = re.search(r"```html(.*?)```", html_content, re.DOTALL)

    if matches:
        # Print the extracted content
        extracted_content = matches.group(1)
        print(extracted_content)

        # Save the extracted content to the "generated_website.html" file
        file_path = os.path.join(templates_dir, "generated_website.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(extracted_content)

        return extracted_content
    else:
        print("No content found between triple single quotes.")

        # Save the original content to the "generated_website.html" file
        file_path = os.path.join(templates_dir, "generated_website.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        return html_content


# Example usage:
# html_content = """Sure, here is how you'd add cards to your website. I've included 3 sample cards.
# ...
#   </div>
# </body>
# </html>
# """
# print(filter_code(html_content))
