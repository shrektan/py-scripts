# model.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from shiny import App, ui, reactive, render

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


# SQLite database
engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# app.py

# app.py

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_text("name", "Name"),
            ui.input_numeric("age", "Age", value=20),
            ui.input_action_button("add_user", "Add User"),
            ui.input_action_button("show_users", "Show Users"),
        ),
        ui.panel_main(
            ui.output_text_verbatim(
                "user_table"
            )  # Make sure this ID matches in the server function
        ),
    )
)


def server(input, output, session):
    @reactive.Effect
    def _():
        if input.add_user() > 0:
            with Session() as db_session:
                new_user = User(name=input.name(), age=input.age())
                db_session.add(new_user)
                db_session.commit()
                print(f'Added user "{input.name()}" with age {input.age()}')

    @output
    @render.text
    def user_table():
        if input.show_users() > 0:
            with Session() as db_session:
                users = db_session.query(User).all()
                return "\n".join([f"{user.name}, {user.age}" for user in users])


app = App(app_ui, server)
