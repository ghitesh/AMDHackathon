import subprocess


class GraphvizLayoutRunner:

    def generate_xdot(
        self,
        dot_string: str
    ) -> str:

        result = subprocess.run(
            ["dot", "-Txdot"],
            input=dot_string,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout
