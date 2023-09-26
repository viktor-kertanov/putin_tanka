db_model:
	@python3 -m db.model

full_news_parser:
	@python3 -m web_parser.kremlin_full_news_parser

title_news_parser:
	@python3 -m web_parser.kremlin_titles_parser