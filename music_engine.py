from audio import play_note, play_chord


class MusicEngine:


    def play_note_event(
            self,
            note,
            state,
            volume=0.4
    ):


        # 主旋律

        main = state.get_instrument()

        play_note(
            note,
            main,
            volume
        )



        # 和弦

        chord = self.build_chord(
            note,
            state
        )


        play_chord(
            chord,
            state.get_accompaniment(),
            0.02
        )



        # Bass

        # 低音

        bass_note = max(
            note - 12,
            36
        )

        play_note(
            bass_note,
            "bass",
            0.04
        )



    def build_chord(
            self,
            note,
            state
    ):

        scale = state.get_scale()


        if scale == "MAJOR":

            return [
                note,
                note+4,
                note+7
            ]


        elif scale == "MINOR":

            return [
                note,
                note+3,
                note+7
            ]


        elif scale == "PENTATONIC":

            return [
                note,
                note+5,
                note+9
            ]