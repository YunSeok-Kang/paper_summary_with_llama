def build_llm_input(full_content):
    summarization_input = ""
    if type(full_content) is not str:
        for _, section in full_content.items():
            if section["title"] == "No title found":
                continue
            if section["content"] == "":
                continue

            summarization_input += (
                f"Section: {section['title']}\n{section['content']}\n\n"
            )

    return summarization_input