from attr import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseBeforeGenerationModule
from griptape.utils import J2


@define
class MetadataGenerationModule(BaseBeforeGenerationModule):
    metadata: str = field(kw_only=True)

    def run(self, context: RagContext) -> RagContext:
        metadata = self.metadata or context.metadata

        context.before_query.append(J2("data/modules/metadata/system.j2").render(metadata=metadata))

        return context
