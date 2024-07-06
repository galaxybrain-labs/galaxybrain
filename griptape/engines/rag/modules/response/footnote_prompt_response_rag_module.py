from attrs import define
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import PromptResponseRagModule
from griptape.utils import J2


@define(kw_only=True)
class FootnotePromptResponseRagModule(PromptResponseRagModule):
    def default_system_template_generator(self, context: RagContext) -> str:
        return J2("engines/rag/modules/response/footnote_prompt/system.j2").render(
            text_chunk_artifacts=context.text_chunks,
            references=context.get_references(),
            before_system_prompt="\n\n".join(context.before_query),
            after_system_prompt="\n\n".join(context.after_query),
        )