import re

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')


def normalise(text: str):
    return re.compile(r"\n\s*").sub("", text)


def is_duplicate(text_one: str, text_two: str) -> bool:
    sentences_one: list[str] = normalise(text_one).split(".")
    sentences_two: list[str] = normalise(text_two).split(".")
    embeddings_one = model.encode(sentences_one, convert_to_tensor=True)
    embeddings_two = model.encode(sentences_two, convert_to_tensor=True)
    similarities = []
    for embedding_one, embedding_two in zip(embeddings_one, embeddings_two):
        similarities.append(*util.pytorch_cos_sim(embedding_one, embedding_two))
    # TODO: fiddle with this, see if it is actually the best way to do it
    if len(sentences_one) == 2 and len(sentences_two) == 2:
        # it is a sentence and not a paragraph
        return sum(similarities) / len(similarities) >= 0.85
    # check if number of cases where similarity is >= 0.85 is >= half the length of total
    return len([x for x in similarities if x >= 0.85]) / len(similarities) >= 0.5
