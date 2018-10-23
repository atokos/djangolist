import schedule

from .models import Auction


def job(self):
    print("Starting auction resolve cron job...")
    due_auctions = Auction.objects.get_all_due()
    for auction in due_auctions:
        if auction.get_latest_bidder() is not None:
            print("Resolving auction %d" % auction.title)

            title = auction.title
            seller = auction.seller
            winner = auction.get_latest_bidder()
            winning_bid = auction.get_latest_bid_amount()

            seller_subject = "Your auction %d has been resolved" % title
            seller_body = "Congratulations, your auction has been resolved!\n\nThe winner is %d, with a bid of %d €" % winner, winning_bid

            winner_subject = "You have won the auction %d" % title
            winner_body = "Congratulations, you have won the auction %d with your bid of %d" % title, winning_bid

            loser_subject = "The Auction %d has been resolved." % title
            loser_body = "Unfortunately, the auction %d that you bid on was won by someone else." % title

            losers = Auction.objects.get_losers()

            for loser in losers:
                loser.email_user(loser_subject, loser_body)
            seller.email_user(seller_subject, seller_body)
            winner.email_user(winner_subject, winner_body)

        # The auction has no bids
        else:
            seller = auction.seller
            subject = "Your auction %d ended with no bids." % title
            body = "Unfortunately, your auction %d did not get any bids, and has now expired." % title
            seller.email_user(subject, body)
