from flask import Flask


def test_service_crud_and_filters(app: Flask):
    researcher_service = app.config["RESEARCHER_SERVICE"]
    paper_service = app.config["PAPER_SERVICE"]

    researcher_id = researcher_service.insert_researcher(
        "Grace Hopper",
        "grace.xml",
        "hash-grace",
        "789",
        nationality="Brasil",
    )

    paper_id = paper_service.add_paper(
        "Compilers and Software Engineering",
        researcher_id,
        year=2025,
        country="Brasil",
    )

    researchers = researcher_service.list_all({"full_name": "Grace"})
    assert len(researchers) == 1
    assert researchers[0].id == researcher_id

    paper = paper_service.get_by_id(paper_id)
    assert paper is not None
    assert paper.title == "Compilers and Software Engineering"

    patched = paper_service.patch(paper_id, {"country": "Portugal"})
    assert patched is not None
    assert patched.country == "Portugal"

    assert paper_service.remove_by_id(paper_id) == 1
    assert researcher_service.remove_by_id(researcher_id) == 1
